import pytest
from backend.app.graph.state import RepairState, AttemptRecord


def test_repair_state_structure():
    state: RepairState = {
        "task_id": "rep_123",
        "workspace_id": "ws_123",
        "workspace_path": "/tmp/ws",
        "source_file": "module.py",
        "test_file": "test_target.py",
        "target_test": "test_target.py::test_fn",
        "regression_files": ["test_regression.py"],
        "original_code": "def foo(): pass",
        "current_code": "def foo(): pass",
        "current_diff": "",
        "coder_plan": "fix bug",
        "coder_summary": "hypothesis",
        "target_test_result": {"passed": False},
        "regression_result": {"passed": True},
        "critic_analysis": "Needs revision",
        "critic_verdict": "REVISE",
        "critic_confidence": 0.9,
        "attempt": 1,
        "max_attempts": 3,
        "failure_type": "TEST_FAILURE",
        "root_cause": "bug",
        "attempts": [],
        "errors": [],
        "workspace_checkpoint_id": "ckpt_1",
        "status": "RUNNING",
        "trace_id": "tr_123",
        "trace_url": None,
        "messages": [],
        "pending_tool_calls": [],
        "tool_round": 0,
        "max_tool_rounds": 4,
    }
    assert state["task_id"] == "rep_123"
    assert state["attempt"] == 1
    assert state["critic_verdict"] == "REVISE"
