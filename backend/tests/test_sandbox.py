import pytest
from backend.app.sandbox.local_sandbox import LocalSandbox
from backend.app.services.workspace_mgr import WorkspaceManager


def test_sandbox_passing_test(tmp_path):
    files = {
        "math_module.py": "def add(a, b): return a + b\n",
        "test_math.py": "from math_module import add\ndef test_add(): assert add(2, 3) == 5\n",
    }
    ws = WorkspaceManager.create_workspace("test_sb_pass", files)
    sandbox = LocalSandbox()

    res = sandbox.execute_test(ws, "test_math.py")
    assert res.passed is True
    assert res.exit_code == 0
    assert res.failure_type == "NONE"

    WorkspaceManager.cleanup_workspace(ws)


def test_sandbox_assertion_failure(tmp_path):
    files = {
        "math_module.py": "def add(a, b): return a * b\n",  # Bug!
        "test_math.py": "from math_module import add\ndef test_add(): assert add(2, 3) == 5\n",
    }
    ws = WorkspaceManager.create_workspace("test_sb_fail", files)
    sandbox = LocalSandbox()

    res = sandbox.execute_test(ws, "test_math.py")
    assert res.passed is False
    assert res.failure_type == "ASSERTION_ERROR"
    assert "assert " in res.stdout or "FAILED" in res.stdout

    WorkspaceManager.cleanup_workspace(ws)


def test_sandbox_syntax_error(tmp_path):
    files = {
        "math_module.py": "def add(a, b): return a + \n",  # SyntaxError!
        "test_math.py": "from math_module import add\ndef test_add(): assert add(2, 3) == 5\n",
    }
    ws = WorkspaceManager.create_workspace("test_sb_syn", files)
    sandbox = LocalSandbox()

    res = sandbox.execute_test(ws, "test_math.py")
    assert res.passed is False
    assert res.failure_type == "SYNTAX_ERROR"

    WorkspaceManager.cleanup_workspace(ws)
