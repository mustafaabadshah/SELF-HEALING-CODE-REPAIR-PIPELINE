import time
import json
import logging
from typing import Dict, Any
from backend.app.graph.state import RepairState
from backend.app.services.workspace_mgr import WorkspaceManager
from backend.app.services.event_bus import event_bus
from backend.app.tools.executor import ToolExecutor
from backend.app.agents.coder import CoderAgent
from backend.app.agents.critic import CriticAgent
from backend.app.observability.langfuse_tracer import LangfuseTracer

logger = logging.getLogger("graph.nodes")


def initialize_repair_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: initialize_repair")
    
    # Trace initialization
    trace = LangfuseTracer.create_trace(task_id, metadata={"source_file": state["source_file"]})
    trace_url = LangfuseTracer.get_trace_url(task_id)

    # Initial checkpoint
    ckpt_id = WorkspaceManager.create_checkpoint(state["workspace_path"], "Initial clean workspace")

    return {
        "status": "RUNNING",
        "attempt": 1,
        "workspace_checkpoint_id": ckpt_id,
        "trace_id": task_id,
        "trace_url": trace_url,
        "attempts": [],
        "errors": [],
        "tool_round": 0,
        "max_tool_rounds": 4,
    }


def inspect_workspace_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: inspect_workspace")

    # Read current files
    try:
        source_code = WorkspaceManager.read_file(state["workspace_path"], state["source_file"])
    except Exception as e:
        source_code = state.get("original_code", "")

    return {
        "original_code": source_code,
        "current_code": source_code,
        "current_diff": "",
    }


def analyze_failure_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: analyze_failure")

    executor = ToolExecutor(
        workspace_path=state["workspace_path"],
        target_test_spec=state["target_test"],
        regression_test_files=state.get("regression_files", []),
    )

    # Run initial target test to observe baseline failure
    initial_target_res = executor.execute("run_target_test", {"test_path": state["target_test"]})

    failure_type = initial_target_res.get("failure_type", "TEST_FAILURE")
    root_cause = initial_target_res.get("error_summary", "Baseline test failure")

    return {
        "target_test_result": initial_target_res,
        "failure_type": failure_type,
        "root_cause": root_cause,
    }


def coder_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    attempt = state["attempt"]
    logger.info(f"[{task_id}] Node: coder (attempt {attempt})")

    agent = CoderAgent()
    start_t = time.time()
    res = agent.run(state)
    duration_ms = int((time.time() - start_t) * 1000)

    tool_calls = res.get("tool_calls", [])

    return {
        "status": "SELF_CORRECTING" if attempt > 1 else "RUNNING",
        "coder_plan": res.get("plan", ""),
        "coder_summary": res.get("hypothesis", ""),
        "pending_tool_calls": tool_calls,
        "tool_round": state.get("tool_round", 0) + 1,
    }


def execute_tool_calls_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: execute_tool_calls")

    executor = ToolExecutor(
        workspace_path=state["workspace_path"],
        target_test_spec=state["target_test"],
        regression_test_files=state.get("regression_files", []),
    )

    tool_calls = state.get("pending_tool_calls", [])
    executed_results = []

    for tc in tool_calls:
        fn_name = tc.get("function", {}).get("name", "")
        raw_args = tc.get("function", {}).get("arguments", "{}")
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except Exception:
            args = {}

        result = executor.execute(fn_name, args)
        executed_results.append({"tool": fn_name, "args": args, "result": result})

    # Read updated code and diff
    try:
        updated_code = WorkspaceManager.read_file(state["workspace_path"], state["source_file"])
    except Exception:
        updated_code = state.get("current_code", "")

    current_diff = WorkspaceManager.get_diff(state["workspace_path"])

    return {
        "current_code": updated_code,
        "current_diff": current_diff,
        "pending_tool_calls": [],  # Clear pending
    }


def target_test_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: target_test")

    executor = ToolExecutor(
        workspace_path=state["workspace_path"],
        target_test_spec=state["target_test"],
        regression_test_files=state.get("regression_files", []),
    )

    target_res = executor.execute("run_target_test", {"test_path": state["target_test"]})

    return {
        "target_test_result": target_res,
        "failure_type": target_res.get("failure_type", "NONE" if target_res.get("passed") else "TEST_FAILURE"),
    }


def regression_test_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: regression_test")

    executor = ToolExecutor(
        workspace_path=state["workspace_path"],
        target_test_spec=state["target_test"],
        regression_test_files=state.get("regression_files", []),
    )

    reg_res = executor.execute("run_regression_tests", {})

    return {
        "regression_result": reg_res,
    }


def critic_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    attempt = state["attempt"]
    logger.info(f"[{task_id}] Node: critic (attempt {attempt})")

    critic = CriticAgent()
    start_t = time.time()
    res = critic.run(state)
    duration_ms = int((time.time() - start_t) * 1000)

    # Record this attempt in shared working memory
    attempt_record = {
        "attempt": attempt,
        "hypothesis": state.get("coder_summary", ""),
        "coder_plan": state.get("coder_plan", ""),
        "diff": state.get("current_diff", ""),
        "target_test_passed": state.get("target_test_result", {}).get("passed", False),
        "regression_passed": state.get("regression_result", {}).get("passed", False),
        "critic_verdict": res.get("verdict", "REVISE"),
        "critic_analysis": res.get("analysis", ""),
        "failure_type": state.get("failure_type", ""),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "latency_ms": duration_ms,
        "input_tokens": res.get("tokens", {}).get("input", 0),
        "output_tokens": res.get("tokens", {}).get("output", 0),
    }

    current_attempts = list(state.get("attempts", []))
    current_attempts.append(attempt_record)

    return {
        "critic_verdict": res.get("verdict", "REVISE"),
        "critic_confidence": res.get("confidence", 0.9),
        "critic_analysis": res.get("analysis", ""),
        "root_cause": res.get("root_cause", state.get("root_cause", "")),
        "attempts": current_attempts,
    }


def route_decision_node(state: RepairState) -> Dict[str, Any]:
    """Pure passthrough node to act as branching hub for conditional edges."""
    return {}


def rollback_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    next_attempt = state["attempt"] + 1
    logger.info(f"[{task_id}] Node: rollback -> resetting to baseline, increment attempt to {next_attempt}")

    # Roll back workspace to clean baseline checkpoint for next attempt
    if state.get("workspace_checkpoint_id"):
        WorkspaceManager.rollback(state["workspace_path"], state["workspace_checkpoint_id"])

    # Read restored code
    try:
        restored_code = WorkspaceManager.read_file(state["workspace_path"], state["source_file"])
    except Exception:
        restored_code = state.get("original_code", "")

    return {
        "attempt": next_attempt,
        "current_code": restored_code,
        "current_diff": "",
        "status": "SELF_CORRECTING",
        "tool_round": 0,
    }


def human_escalation_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: human_escalation")

    return {
        "status": "HUMAN_REVIEW",
    }


def finalize_success_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: finalize_success")

    return {
        "status": "SUCCESS",
    }


def finalize_failure_node(state: RepairState) -> Dict[str, Any]:
    task_id = state["task_id"]
    logger.info(f"[{task_id}] Node: finalize_failure")

    return {
        "status": "FAILED",
    }
