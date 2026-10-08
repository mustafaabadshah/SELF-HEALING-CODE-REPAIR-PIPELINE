import os
import shutil
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, List
import git
from backend.app.config import settings


class SecurityError(Exception):
    pass


class WorkspaceManager:
    @staticmethod
    def _validate_path(workspace_path: Path, relative_path: str) -> Path:
        """Enforce strict workspace isolation and prevent path traversal."""
        # Clean relative path
        rel = Path(relative_path)
        if rel.is_absolute():
            raise SecurityError(f"Absolute paths not permitted: {relative_path}")

        target = (workspace_path / rel).resolve()
        ws_resolved = workspace_path.resolve()

        try:
            target.relative_to(ws_resolved)
        except ValueError:
            raise SecurityError(f"Path traversal detected: {relative_path} attempts to escape {workspace_path}")

        return target

    @classmethod
    def create_workspace(cls, repair_id: str, files: Dict[str, str]) -> str:
        """
        Creates an isolated temporary workspace for the repair run,
        writes initial files, and initializes a local git repository for checkpointing.
        """
        ws_dir = Path(settings.workspace_root) / repair_id
        if ws_dir.exists():
            shutil.rmtree(ws_dir, ignore_errors=True)
        ws_dir.mkdir(parents=True, exist_ok=True)

        # Write files
        for rel_path, content in files.items():
            file_path = cls._validate_path(ws_dir, rel_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        # Initialize git repo for reliable diff and rollback tracking
        try:
            repo = git.Repo.init(ws_dir)
            repo.config_writer().set_value("user", "name", "SelfHealingAgent").release()
            repo.config_writer().set_value("user", "email", "agent@self-healing.ai").release()
            repo.git.add(A=True)
            repo.index.commit("Initial workspace state")
        except Exception as e:
            # Fallback if git binary has issues
            pass

        return str(ws_dir)

    @classmethod
    def create_checkpoint(cls, workspace_path: str, message: str = "Checkpoint") -> str:
        """Creates a git commit checkpoint and returns its commit hash."""
        ws_path = Path(workspace_path)
        try:
            repo = git.Repo(ws_path)
            repo.git.add(A=True)
            # Only commit if there are changes
            if repo.is_dirty(untracked_files=True):
                commit = repo.index.commit(message)
                return commit.hexsha
            else:
                return repo.head.commit.hexsha
        except Exception:
            # Fallback hash
            return f"ckpt_{int(time.time())}"

    @classmethod
    def rollback(cls, workspace_path: str, checkpoint_id: str) -> bool:
        """Rollback workspace to a specific checkpoint hash or commit."""
        ws_path = Path(workspace_path)
        try:
            repo = git.Repo(ws_path)
            repo.git.reset("--hard", checkpoint_id)
            repo.git.clean("-fd")
            return True
        except Exception:
            return False

    @classmethod
    def get_diff(cls, workspace_path: str) -> str:
        """Returns unified git diff against the initial commit or working tree."""
        ws_path = Path(workspace_path)
        try:
            repo = git.Repo(ws_path)
            # Diff against HEAD or initial commit
            diff_text = repo.git.diff("HEAD~0")
            if not diff_text:
                # Check untracked or staged
                diff_text = repo.git.diff()
            if not diff_text and len(repo.iter_commits()) > 1:
                # Diff between first commit and HEAD
                first_commit = list(repo.iter_commits())[-1]
                diff_text = repo.git.diff(first_commit.hexsha, "HEAD")
            return diff_text or ""
        except Exception:
            return ""

    @classmethod
    def read_file(cls, workspace_path: str, relative_path: str) -> str:
        ws_path = Path(workspace_path)
        target = cls._validate_path(ws_path, relative_path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return target.read_text(encoding="utf-8")

    @classmethod
    def write_file(cls, workspace_path: str, relative_path: str, content: str) -> None:
        ws_path = Path(workspace_path)
        target = cls._validate_path(ws_path, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    @classmethod
    def list_files(cls, workspace_path: str, directory: str = ".") -> List[str]:
        ws_path = Path(workspace_path)
        target_dir = cls._validate_path(ws_path, directory)
        if not target_dir.is_dir():
            return []

        rel_files = []
        for p in target_dir.rglob("*"):
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ws_path).parts):
                rel_files.append(str(p.relative_to(ws_path)).replace("\\", "/"))
        return sorted(rel_files)

    @classmethod
    def get_file_metadata(cls, workspace_path: str, relative_path: str) -> dict:
        ws_path = Path(workspace_path)
        target = cls._validate_path(ws_path, relative_path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        stat = target.stat()
        content = target.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()

        return {
            "path": relative_path,
            "size_bytes": stat.st_size,
            "language": "python" if relative_path.endswith(".py") else "text",
            "modified_time": stat.st_mtime,
            "sha256": sha256,
        }

    @classmethod
    def cleanup_workspace(cls, workspace_path: str) -> None:
        try:
            ws_path = Path(workspace_path)
            if ws_path.exists():
                shutil.rmtree(ws_path, ignore_errors=True)
        except Exception:
            pass
