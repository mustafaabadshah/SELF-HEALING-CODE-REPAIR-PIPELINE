import pytest
from pathlib import Path
from backend.app.config import settings
from backend.app.graph.workflow import repair_graph
from backend.app.services.workspace_mgr import WorkspaceManager


def test_repair_graph_execution_with_mock_agent(tmp_path):
    settings.mock_llm = True

    demo_dir = Path(__file__).resolve().parent.parent.parent / "examples" / "regression_demo"
    source = (demo_dir / "buggy_module.py").read_text(encoding="utf-8")
    target_test = (demo_dir / "test_target.py").read_text(encoding="utf-8")
    regression_test = (demo_dir / "test_regression.py").read_text(encoding="utf-8")

    repair_id = "test_int_graph"
    files = {
        "buggy_module.py": source,
        "test_target.py": target_test,
        "test_regression.py": regression_test,
    }
    ws_path = WorkspaceManager.create_workspace(repair_id, files)

    initial_state = {
        "task_id": repair_id,
        "workspace_id": repair_id,
        "workspace_path": ws_path,
        "source_file": "buggy_module.py",
        "test_file": "test_target.py",
        "target_test": "test_target.py::test_discount_with_percentage_string",
        "regression_files": ["test_regression.py"],
        "original_code": source,
        "current_code": source,
        "current_diff": "",
        "coder_plan": "",
        "coder_summary": "",
        "target_test_result": {},
        "regression_result": {},
        "critic_analysis": "",
        "critic_verdict": "",
        "critic_confidence": None,
        "attempt": 1,
        "max_attempts": 3,
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

    final_state = repair_graph.invoke(initial_state)

    assert final_state["status"] == "SUCCESS"
    assert len(final_state["attempts"]) == 2
    # Attempt 1: Target PASS, Regression FAIL, Critic REVISE
    att1 = final_state["attempts"][0]
    assert att1["attempt"] == 1
    assert att1["target_test_passed"] is True
    assert att1["regression_passed"] is False
    assert att1["critic_verdict"] == "REVISE"

    # Attempt 2: Target PASS, Regression PASS, Critic PASS
    att2 = final_state["attempts"][1]
    assert att2["attempt"] == 2
    assert att2["target_test_passed"] is True
    assert att2["regression_passed"] is True
    assert att2["critic_verdict"] == "PASS"

    WorkspaceManager.cleanup_workspace(ws_path)
