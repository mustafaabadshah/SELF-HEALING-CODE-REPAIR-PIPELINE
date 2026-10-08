import pytest
from pathlib import Path
from backend.app.services.workspace_mgr import WorkspaceManager, SecurityError
from backend.app.tools.patch_engine import apply_patch_to_text, PatchError


def test_path_traversal_blocked(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    # Attempt to access outside parent directory
    with pytest.raises(SecurityError):
        WorkspaceManager.read_file(str(ws), "../secret.txt")

    with pytest.raises(SecurityError):
        WorkspaceManager.read_file(str(ws), "../../etc/passwd")


def test_absolute_path_blocked(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()

    with pytest.raises(SecurityError):
        WorkspaceManager.read_file(str(ws), "C:/Windows/System32/cmd.exe")


def test_syntax_validation_catches_invalid_python():
    orig_code = "def calculate():\n    return 42\n"
    bad_patch = "<<<<<<< SEARCH\n    return 42\n=======\n    return 42 +\n>>>>>>> REPLACE"

    with pytest.raises(PatchError) as exc_info:
        apply_patch_to_text(orig_code, bad_patch, filename="test_module.py")

    assert "Syntax error" in str(exc_info.value)


def test_valid_patch_applies_cleanly():
    orig_code = "def greet(name):\n    return 'Hello ' + name\n"
    patch = "<<<<<<< SEARCH\n    return 'Hello ' + name\n=======\n    return f'Welcome, {name}!'\n>>>>>>> REPLACE"

    new_code, stats = apply_patch_to_text(orig_code, patch, filename="greet.py")
    assert "Welcome, {name}!" in new_code
    assert stats["lines_added"] >= 1
    assert stats["lines_removed"] >= 1
