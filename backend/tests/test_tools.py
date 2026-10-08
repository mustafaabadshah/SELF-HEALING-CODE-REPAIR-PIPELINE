import pytest
from pathlib import Path
from backend.app.services.workspace_mgr import WorkspaceManager
from backend.app.tools.executor import ToolExecutor


def test_tool_executor_file_operations(tmp_path):
    ws = tmp_path / "ws_test"
    files = {"foo.py": "def foo(): return 1\n"}
    ws_path = WorkspaceManager.create_workspace("test_rep", files)

    executor = ToolExecutor(workspace_path=ws_path, target_test_spec="test_foo.py")

    # read_file
    res_read = executor.execute("read_file", {"path": "foo.py"})
    assert res_read["content"] == "def foo(): return 1\n"

    # list_files
    res_list = executor.execute("list_files", {})
    assert "foo.py" in res_list["files"]

    # apply_patch
    patch = "<<<<<<< SEARCH\ndef foo(): return 1\n=======\ndef foo(): return 2\n>>>>>>> REPLACE"
    res_patch = executor.execute("apply_patch", {"path": "foo.py", "patch": patch})
    assert res_patch["success"] is True

    # get_diff
    res_diff = executor.execute("get_diff", {})
    assert "-def foo(): return 1" in res_diff["diff"]
    assert "+def foo(): return 2" in res_diff["diff"]

    WorkspaceManager.cleanup_workspace(ws_path)
