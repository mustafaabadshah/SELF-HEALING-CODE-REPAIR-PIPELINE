import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, Query
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import (
    CreateRepairRequest,
    CreateRepairResponse,
    RepairDetailResponse,
    AttemptSummary,
    DiffResponse,
    TraceResponse,
    EscalationDecisionRequest,
    DashboardMetrics,
    ScanDirectoryRequest,
    ScanDirectoryResponse,
    ScannedFile,
    PresetItem,
    RegressionFilePayload,
)
from backend.app.services.repair_service import RepairService
from backend.app.services.event_bus import event_bus
from backend.app.api.websocket import handle_repair_websocket

router = APIRouter(prefix="/api")


@router.post("/repairs", response_model=CreateRepairResponse)
async def create_repair(request: CreateRepairRequest):
    try:
        repair_id = await RepairService.create_repair(request)
        return CreateRepairResponse(
            repair_id=repair_id,
            status="QUEUED",
            message="Repair pipeline initiated successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repairs", response_model=List[RepairDetailResponse])
async def list_repairs(limit: int = Query(50, ge=1, le=100)):
    records = await RepairService.list_repairs(limit=limit)
    response = []
    for r in records:
        attempts = [
            AttemptSummary(
                id=a.id,
                attempt_number=a.attempt_number,
                hypothesis=a.hypothesis,
                diff=a.diff,
                target_passed=a.target_passed,
                regression_passed=a.regression_passed,
                critic_verdict=a.critic_verdict,
                critic_analysis=a.critic_analysis,
                critic_confidence=a.critic_confidence,
                failure_type=a.failure_type,
                latency_ms=a.latency_ms,
                input_tokens=a.input_tokens,
                output_tokens=a.output_tokens,
                created_at=a.created_at,
            )
            for a in (r.attempts or [])
        ]
        response.append(
            RepairDetailResponse(
                id=r.id,
                status=r.status,
                source_file=r.source_file,
                test_file=r.test_file,
                target_test=r.target_test,
                max_attempts=r.max_attempts,
                current_attempt=r.current_attempt,
                trace_id=r.trace_id,
                trace_url=r.trace_url,
                error_message=r.error_message,
                final_diff=r.final_diff,
                created_at=r.created_at,
                updated_at=r.updated_at,
                attempts=attempts,
            )
        )
    return response


@router.get("/repairs/{repair_id}", response_model=RepairDetailResponse)
async def get_repair(repair_id: str):
    record = await RepairService.get_repair(repair_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")

    attempts = [
        AttemptSummary(
            id=a.id,
            attempt_number=a.attempt_number,
            hypothesis=a.hypothesis,
            diff=a.diff,
            target_passed=a.target_passed,
            regression_passed=a.regression_passed,
            critic_verdict=a.critic_verdict,
            critic_analysis=a.critic_analysis,
            critic_confidence=a.critic_confidence,
            failure_type=a.failure_type,
            latency_ms=a.latency_ms,
            input_tokens=a.input_tokens,
            output_tokens=a.output_tokens,
            created_at=a.created_at,
        )
        for a in (record.attempts or [])
    ]

    return RepairDetailResponse(
        id=record.id,
        status=record.status,
        source_file=record.source_file,
        test_file=record.test_file,
        target_test=record.target_test,
        max_attempts=record.max_attempts,
        current_attempt=record.current_attempt,
        trace_id=record.trace_id,
        trace_url=record.trace_url,
        error_message=record.error_message,
        final_diff=record.final_diff,
        created_at=record.created_at,
        updated_at=record.updated_at,
        attempts=attempts,
    )


@router.get("/repairs/{repair_id}/events")
async def stream_repair_events(repair_id: str, sse: bool = False):
    """Returns event stream as Server-Sent Events (SSE) or historical JSON."""
    if not sse:
        return event_bus.get_history(repair_id)

    async def event_generator():
        queue = event_bus.subscribe(repair_id)
        # Replay history first
        for evt in event_bus.get_history(repair_id):
            yield f"data: {json.dumps(evt)}\n\n"

        try:
            while True:
                evt = await queue.get()
                yield f"data: {json.dumps(evt)}\n\n"
        finally:
            event_bus.unsubscribe(repair_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.websocket("/repairs/{repair_id}/ws")
async def websocket_endpoint(websocket: WebSocket, repair_id: str):
    await handle_repair_websocket(websocket, repair_id)


@router.get("/repairs/{repair_id}/attempts", response_model=List[AttemptSummary])
async def get_repair_attempts(repair_id: str):
    record = await RepairService.get_repair(repair_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")

    return [
        AttemptSummary(
            id=a.id,
            attempt_number=a.attempt_number,
            hypothesis=a.hypothesis,
            diff=a.diff,
            target_passed=a.target_passed,
            regression_passed=a.regression_passed,
            critic_verdict=a.critic_verdict,
            critic_analysis=a.critic_analysis,
            critic_confidence=a.critic_confidence,
            failure_type=a.failure_type,
            latency_ms=a.latency_ms,
            input_tokens=a.input_tokens,
            output_tokens=a.output_tokens,
            created_at=a.created_at,
        )
        for a in (record.attempts or [])
    ]


@router.get("/repairs/{repair_id}/diff", response_model=DiffResponse)
async def get_repair_diff(repair_id: str):
    diff_data = await RepairService.get_diff(repair_id)
    return DiffResponse(**diff_data)


@router.get("/repairs/{repair_id}/tests")
async def get_repair_tests(repair_id: str):
    record = await RepairService.get_repair(repair_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")

    tests = []
    for att in (record.attempts or []):
        for tr in (att.test_runs or []):
            tests.append({
                "attempt": att.attempt_number,
                "type": tr.type,
                "passed": tr.passed,
                "exit_code": tr.exit_code,
                "duration_ms": tr.duration_ms,
                "stdout": tr.stdout,
                "stderr": tr.stderr,
                "failure_type": tr.failure_type,
            })
    return tests


@router.get("/repairs/{repair_id}/trace", response_model=TraceResponse)
async def get_repair_trace(repair_id: str):
    record = await RepairService.get_repair(repair_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")

    return TraceResponse(
        repair_id=repair_id,
        trace_id=record.trace_id,
        trace_url=record.trace_url,
    )


@router.post("/repairs/{repair_id}/escalation")
async def handle_escalation_decision(repair_id: str, req: EscalationDecisionRequest):
    try:
        return await RepairService.handle_escalation(repair_id, req.decision, req.comment or "")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics():
    return await RepairService.get_dashboard_metrics()


@router.get("/demo/preload")
async def preload_demo_data():
    """Returns pre-loaded source and test code for the built-in regression demo."""
    demo_dir = Path(__file__).resolve().parent.parent.parent.parent / "examples" / "regression_demo"

    source = (demo_dir / "buggy_module.py").read_text(encoding="utf-8")
    target_test = (demo_dir / "test_target.py").read_text(encoding="utf-8")
    regression_test = (demo_dir / "test_regression.py").read_text(encoding="utf-8")

    return {
        "source_file": "buggy_module.py",
        "source_content": source,
        "test_file": "test_target.py",
        "test_content": target_test,
        "target_test": "test_target.py::test_discount_with_percentage_string",
        "regression_tests": [
            {
                "filename": "test_regression.py",
                "content": regression_test,
            }
        ],
        "max_attempts": 3,
    }


def extract_test_cases_from_code(content: str) -> List[str]:
    """Extracts function names starting with test_ using AST or regex fallback."""
    import ast
    try:
        tree = ast.parse(content)
        tests = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tests.append(node.name)
        return tests
    except Exception:
        import re
        return re.findall(r"def (test_\w+)\s*\(", content)


@router.post("/workspace/scan-directory", response_model=ScanDirectoryResponse)
async def scan_local_directory(req: ScanDirectoryRequest):
    """
    Scans a local folder on the user's computer for Python source files and test suites.
    Categorizes files into candidate source files and test files, extracting test cases.
    """
    clean_path = req.directory_path.strip().strip('"').strip("'")
    if not clean_path:
        raise HTTPException(status_code=400, detail="Directory path cannot be empty")

    p = Path(clean_path).resolve()
    if not p.exists():
        raise HTTPException(status_code=400, detail=f"Directory path does not exist: {clean_path}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {clean_path}")

    source_files = []
    test_files = []

    # Recursively find .py files
    for file_path in p.rglob("*.py"):
        parts = file_path.parts
        # Skip virtual envs, git, cache, node
        if any(ign in parts for ign in (".git", "venv", ".venv", "__pycache__", "node_modules", "site-packages", ".pytest_cache")):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        rel_name = file_path.relative_to(p).as_posix()
        fname = file_path.name.lower()

        if fname.startswith("test_") or fname.endswith("_test.py"):
            test_cases = extract_test_cases_from_code(content)
            test_files.append(
                ScannedFile(
                    filename=rel_name,
                    content=content,
                    test_cases=test_cases,
                )
            )
        else:
            source_files.append(
                ScannedFile(
                    filename=rel_name,
                    content=content,
                    test_cases=[],
                )
            )

    return ScanDirectoryResponse(
        directory_path=str(p),
        source_files=source_files,
        test_files=test_files,
    )


@router.get("/presets", response_model=List[PresetItem])
async def get_presets():
    """
    Returns beginner-friendly, pre-configured repair challenges.
    Allows non-technical users to test self-healing loops with 1 click.
    """
    root = Path(__file__).resolve().parent.parent.parent.parent

    presets = []

    # 1. Regression Demo
    demo_dir = root / "examples" / "regression_demo"
    if (demo_dir / "buggy_module.py").exists():
        src = (demo_dir / "buggy_module.py").read_text(encoding="utf-8")
        tgt = (demo_dir / "test_target.py").read_text(encoding="utf-8")
        reg = (demo_dir / "test_regression.py").read_text(encoding="utf-8")
        presets.append(
            PresetItem(
                id="ecommerce_discount",
                title="🛒 E-Commerce Promo Discount Calculator",
                category="E-Commerce",
                badge="Multi-Turn Regression Demo",
                description="Online checkout crashes with TypeError when promo discount is entered as '20%' string instead of decimal fraction 0.20.",
                layman_story="The AI first naively divides all discounts by 100, which fixes '20%' but accidentally breaks regular 0.20 decimal discounts! The system detects the regression, restores clean code, and heals both on Attempt 2.",
                source_file="buggy_module.py",
                source_content=src,
                test_file="test_target.py",
                test_content=tgt,
                target_test="test_target.py::test_discount_with_percentage_string",
                regression_tests=[RegressionFilePayload(filename="test_regression.py", content=reg)],
                max_attempts=3,
            )
        )

    # 2. Arithmetic Tax
    task1 = root / "benchmarks" / "tasks" / "01_arithmetic_tax"
    if (task1 / "tax_calc.py").exists():
        src = (task1 / "tax_calc.py").read_text(encoding="utf-8")
        tgt = (task1 / "test_target.py").read_text(encoding="utf-8")
        reg = (task1 / "test_regression.py").read_text(encoding="utf-8")
        presets.append(
            PresetItem(
                id="accounting_tax",
                title="🧮 Accounting Sales Tax Calculator",
                category="Finance",
                badge="Boundary Rounding Bug",
                description="Invoice calculator loses fractional cents instead of properly rounding up when round_up=True.",
                layman_story="Standard rounding loses fractional cents on taxable transactions. The AI patches the boundary rounding check so calculations match financial regulations.",
                source_file="tax_calc.py",
                source_content=src,
                test_file="test_target.py",
                test_content=tgt,
                target_test="test_target.py::test_round_up_calculation",
                regression_tests=[RegressionFilePayload(filename="test_regression.py", content=reg)],
                max_attempts=3,
            )
        )

    # 3. Binary Search
    task3 = root / "benchmarks" / "tasks" / "03_boundary_binary_search"
    if (task3 / "search_module.py").exists():
        src = (task3 / "search_module.py").read_text(encoding="utf-8")
        tgt = (task3 / "test_target.py").read_text(encoding="utf-8")
        reg = (task3 / "test_regression.py").read_text(encoding="utf-8")
        presets.append(
            PresetItem(
                id="binary_search_boundary",
                title="🔍 Search Engine Index Finder",
                category="Algorithms",
                badge="Off-By-One Boundary Bug",
                description="Search algorithm fails with -1 when searching for an element located at the exact end of an array.",
                layman_story="A classic off-by-one bug where the loop boundary check excludes the final element. The AI spots the boundary error and fixes the comparison.",
                source_file="search_module.py",
                source_content=src,
                test_file="test_target.py",
                test_content=tgt,
                target_test="test_target.py::test_search_last_element",
                regression_tests=[RegressionFilePayload(filename="test_regression.py", content=reg)],
                max_attempts=3,
            )
        )

    # 4. None User Profile
    task4 = root / "benchmarks" / "tasks" / "04_none_user_profile"
    if (task4 / "user_service.py").exists():
        src = (task4 / "user_service.py").read_text(encoding="utf-8")
        tgt = (task4 / "test_target.py").read_text(encoding="utf-8")
        reg = (task4 / "test_regression.py").read_text(encoding="utf-8")
        presets.append(
            PresetItem(
                id="none_user_profile",
                title="🛡️ Safe User Profile Accessor",
                category="Web Services",
                badge="Null Safety / None Protection",
                description="API crashes with AttributeError when querying optional notification preferences for newly registered users.",
                layman_story="New users don't have secondary profile objects created yet. The AI adds safe attribute traversal so the app never crashes on missing profile keys.",
                source_file="user_service.py",
                source_content=src,
                test_file="test_target.py",
                test_content=tgt,
                target_test="test_target.py::test_new_user_without_preferences",
                regression_tests=[RegressionFilePayload(filename="test_regression.py", content=reg)],
                max_attempts=3,
            )
        )

    return presets

