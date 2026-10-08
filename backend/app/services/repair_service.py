import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from backend.app.config import settings
from backend.app.db.session import async_session
from backend.app.db.models import RepairModel, AttemptModel, TestRunModel, EventModel
from backend.app.services.workspace_mgr import WorkspaceManager
from backend.app.services.event_bus import event_bus
from backend.app.graph.workflow import repair_graph
from backend.app.graph.state import RepairState
from backend.app.models.schemas import CreateRepairRequest, DashboardMetrics

logger = logging.getLogger("services.repair_service")


class RepairService:
    @classmethod
    async def create_repair(cls, req: CreateRepairRequest) -> str:
        repair_id = f"rep_{uuid.uuid4().hex[:10]}"

        # Prepare workspace files
        files = {
            req.source_file: req.source_content,
            req.test_file: req.test_content,
        }
        regression_names = []
        for reg in req.regression_tests:
            files[reg.filename] = reg.content
            regression_names.append(reg.filename)

        # Create isolated workspace on filesystem
        workspace_path = WorkspaceManager.create_workspace(repair_id, files)

        # Insert DB record
        async with async_session() as db:
            repair = RepairModel(
                id=repair_id,
                status="QUEUED",
                source_file=req.source_file,
                test_file=req.test_file,
                target_test=req.target_test,
                max_attempts=req.max_attempts,
                current_attempt=0,
                trace_id=repair_id,
            )
            db.add(repair)
            await db.commit()

        # Publish initial events
        await event_bus.publish(repair_id, "repair.started", {"repair_id": repair_id, "status": "QUEUED"})
        await event_bus.publish(
            repair_id,
            "workspace.created",
            {"workspace_path": workspace_path, "files": list(files.keys())},
        )

        # Prepare initial state for LangGraph
        initial_state: RepairState = {
            "task_id": repair_id,
            "workspace_id": repair_id,
            "workspace_path": workspace_path,
            "source_file": req.source_file,
            "test_file": req.test_file,
            "target_test": req.target_test,
            "regression_files": regression_names,
            "original_code": req.source_content,
            "current_code": req.source_content,
            "current_diff": "",
            "coder_plan": "",
            "coder_summary": "",
            "target_test_result": {},
            "regression_result": {},
            "critic_analysis": "",
            "critic_verdict": "",
            "critic_confidence": None,
            "attempt": 1,
            "max_attempts": req.max_attempts,
            "failure_type": "INITIALIZING",
            "root_cause": "",
            "attempts": [],
            "errors": [],
            "workspace_checkpoint_id": None,
            "status": "RUNNING",
            "trace_id": repair_id,
            "trace_url": None,
            "messages": [],
            "pending_tool_calls": [],
            "tool_round": 0,
            "max_tool_rounds": 4,
        }

        # Override mock mode if requested in payload
        if req.use_mock is not None:
            settings.mock_llm = req.use_mock

        # Launch background runner task
        asyncio.create_task(cls._run_repair_workflow(repair_id, initial_state))

        return repair_id

    @classmethod
    async def _run_repair_workflow(cls, repair_id: str, initial_state: RepairState):
        logger.info(f"Starting LangGraph execution for {repair_id}")

        async with async_session() as db:
            repair = await db.get(RepairModel, repair_id)
            if repair:
                repair.status = "RUNNING"
                await db.commit()

        try:
            # We run the graph synchronously in threadpool to support async FastAPI seamlessly
            final_state = await asyncio.to_thread(repair_graph.invoke, initial_state)

            final_status = final_state.get("status", "COMPLETED")
            attempts_list = final_state.get("attempts", [])
            final_diff = final_state.get("current_diff", "")
            trace_url = final_state.get("trace_url")

            # Persist attempts and test runs to database
            async with async_session() as db:
                repair = await db.get(RepairModel, repair_id)
                if repair:
                    repair.status = final_status
                    repair.current_attempt = len(attempts_list)
                    repair.final_diff = final_diff
                    repair.trace_url = trace_url
                    repair.updated_at = datetime.now(timezone.utc)

                    for att in attempts_list:
                        att_id = f"att_{uuid.uuid4().hex[:10]}"
                        attempt_model = AttemptModel(
                            id=att_id,
                            repair_id=repair_id,
                            attempt_number=att.get("attempt", 1),
                            hypothesis=att.get("hypothesis", ""),
                            coder_plan=att.get("coder_plan", ""),
                            diff=att.get("diff", ""),
                            target_passed=att.get("target_test_passed", False),
                            regression_passed=att.get("regression_passed", False),
                            critic_verdict=att.get("critic_verdict", "REVISE"),
                            critic_analysis=att.get("critic_analysis", ""),
                            failure_type=att.get("failure_type", ""),
                            latency_ms=att.get("latency_ms", 0),
                            input_tokens=att.get("input_tokens", 0),
                            output_tokens=att.get("output_tokens", 0),
                        )
                        db.add(attempt_model)

                        # Add test run records
                        t_res = att.get("target_test_result", {})
                        r_res = att.get("regression_result", {})

                        t_run = TestRunModel(
                            id=f"tr_{uuid.uuid4().hex[:10]}",
                            repair_id=repair_id,
                            attempt_id=att_id,
                            type="TARGET",
                            passed=att.get("target_test_passed", False),
                            exit_code=t_res.get("exit_code", 0 if att.get("target_test_passed") else 1),
                            duration_ms=t_res.get("duration_ms", att.get("latency_ms", 0) // 2),
                            stdout=t_res.get("stdout", ""),
                            stderr=t_res.get("stderr", ""),
                            failure_type=t_res.get("failure_type", "NONE" if att.get("target_test_passed") else "TEST_FAILURE"),
                        )
                        r_run = TestRunModel(
                            id=f"tr_{uuid.uuid4().hex[:10]}",
                            repair_id=repair_id,
                            attempt_id=att_id,
                            type="REGRESSION",
                            passed=att.get("regression_passed", False),
                            exit_code=r_res.get("exit_code", 0 if att.get("regression_passed") else 1),
                            duration_ms=r_res.get("duration_ms", att.get("latency_ms", 0) // 2),
                            stdout=r_res.get("stdout", ""),
                            stderr=r_res.get("stderr", ""),
                            failure_type=r_res.get("failure_type", "NONE" if att.get("regression_passed") else "REGRESSION"),
                        )
                        db.add(t_run)
                        db.add(r_run)

                    await db.commit()

            # Broadcast final events
            if final_status == "SUCCESS":
                await event_bus.publish(
                    repair_id,
                    "repair.success",
                    {
                        "repair_id": repair_id,
                        "status": "SUCCESS",
                        "attempts": len(attempts_list),
                        "diff": final_diff,
                    },
                )
            elif final_status == "HUMAN_REVIEW":
                await event_bus.publish(
                    repair_id,
                    "human_review.required",
                    {
                        "repair_id": repair_id,
                        "status": "HUMAN_REVIEW",
                        "attempts": len(attempts_list),
                        "critic_analysis": final_state.get("critic_analysis", ""),
                    },
                )
            else:
                await event_bus.publish(
                    repair_id,
                    "repair.failed",
                    {"repair_id": repair_id, "status": "FAILED", "errors": final_state.get("errors", [])},
                )

        except Exception as e:
            logger.exception(f"Fatal error in repair graph for {repair_id}: {e}")
            async with async_session() as db:
                repair = await db.get(RepairModel, repair_id)
                if repair:
                    repair.status = "FAILED"
                    repair.error_message = str(e)
                    await db.commit()
            await event_bus.publish(repair_id, "repair.failed", {"error": str(e)})

    @classmethod
    async def get_repair(cls, repair_id: str) -> Optional[RepairModel]:
        async with async_session() as db:
            result = await db.execute(
                select(RepairModel)
                .options(selectinload(RepairModel.attempts).selectinload(AttemptModel.test_runs), selectinload(RepairModel.events))
                .where(RepairModel.id == repair_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def list_repairs(cls, limit: int = 50) -> List[RepairModel]:
        async with async_session() as db:
            result = await db.execute(
                select(RepairModel)
                .options(selectinload(RepairModel.attempts).selectinload(AttemptModel.test_runs))
                .order_by(RepairModel.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    @classmethod
    async def get_diff(cls, repair_id: str) -> Dict[str, Any]:
        async with async_session() as db:
            repair = await db.get(RepairModel, repair_id)
            if not repair:
                return {"diff": "", "files_changed": 0, "lines_added": 0, "lines_removed": 0}

            diff_str = repair.final_diff or ""
            if not diff_str:
                # Try getting directly from workspace
                ws_path = f"{settings.workspace_root}/{repair_id}"
                diff_str = WorkspaceManager.get_diff(ws_path)

            lines = diff_str.splitlines()
            added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
            removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
            files_changed = 1 if diff_str else 0

            return {
                "repair_id": repair_id,
                "diff": diff_str,
                "files_changed": files_changed,
                "lines_added": added,
                "lines_removed": removed,
            }

    @classmethod
    async def handle_escalation(cls, repair_id: str, decision: str, comment: str = "") -> Dict[str, Any]:
        async with async_session() as db:
            repair = await db.get(RepairModel, repair_id)
            if not repair:
                raise ValueError("Repair not found")

            if decision == "APPROVE_PATCH":
                repair.status = "SUCCESS"
                new_status = "SUCCESS"
            elif decision == "REJECT_PATCH":
                repair.status = "FAILED"
                new_status = "FAILED"
            elif decision == "RESET":
                repair.status = "QUEUED"
                new_status = "QUEUED"
            else:
                raise ValueError(f"Invalid decision: {decision}")

            await db.commit()

        await event_bus.publish(
            repair_id,
            f"escalation.{decision.lower()}",
            {"decision": decision, "status": new_status, "comment": comment},
        )

        return {"repair_id": repair_id, "status": new_status, "decision": decision}

    @classmethod
    async def get_dashboard_metrics(cls) -> DashboardMetrics:
        async with async_session() as db:
            total = await db.scalar(select(func.count(RepairModel.id))) or 0
            success = await db.scalar(select(func.count(RepairModel.id)).where(RepairModel.status == "SUCCESS")) or 0
            failed = await db.scalar(select(func.count(RepairModel.id)).where(RepairModel.status == "FAILED")) or 0
            escalated = await db.scalar(select(func.count(RepairModel.id)).where(RepairModel.status == "HUMAN_REVIEW")) or 0
            avg_attempts = await db.scalar(select(func.avg(RepairModel.current_attempt))) or 0.0

            # Attempt tokens & latencies
            total_tokens = await db.scalar(select(func.sum(AttemptModel.input_tokens + AttemptModel.output_tokens))) or 0
            avg_lat = await db.scalar(select(func.avg(AttemptModel.latency_ms))) or 0.0

            # Regressions detected
            regression_attempts = await db.scalar(
                select(func.count(AttemptModel.id)).where(
                    AttemptModel.target_passed == True, AttemptModel.regression_passed == False
                )
            ) or 0
            total_attempts = await db.scalar(select(func.count(AttemptModel.id))) or 0
            reg_rate = (regression_attempts / total_attempts * 100.0) if total_attempts > 0 else 0.0

            return DashboardMetrics(
                total_repairs=total,
                successful_repairs=success,
                failed_repairs=failed,
                escalations=escalated,
                average_attempts=round(float(avg_attempts), 2),
                average_repair_time_ms=round(float(avg_lat), 1),
                regression_rate=round(float(reg_rate), 1),
                total_tokens=int(total_tokens),
                average_latency_ms=round(float(avg_lat), 1),
            )
