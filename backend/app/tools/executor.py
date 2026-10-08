import json
import logging
from typing import Dict, Any, Optional, List
from backend.app.services.workspace_mgr import WorkspaceManager, SecurityError
from backend.app.tools.patch_engine import apply_patch_to_text, PatchError
from backend.app.sandbox.manager import get_sandbox
from backend.app.sandbox.base import TestResult

logger = logging.getLogger("tools.executor")


class ToolExecutor:
    """
    Executes native tool calls issued by LLM agents.
    Enforces security, validates parameters, and interacts safely with workspace and sandbox.
    """

    def __init__(
        self,
        workspace_path: str,
        target_test_spec: str,
        regression_test_files: List[str] = None,
    ):
        self.workspace_path = workspace_path
        self.target_test_spec = target_test_spec
        self.regression_test_files = regression_test_files or []
        self.sandbox = get_sandbox()
        self.checkpoints: Dict[str, str] = {}
        self.latest_test_results: Dict[str, Any] = {}

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a tool call to the appropriate internal method."""
        logger.info(f"Executing tool {tool_name} with args: {args}")

        try:
            if tool_name == "read_file":
                path = args.get("path")
                if not path:
                    return {"error": "Missing required argument 'path'"}
                content = WorkspaceManager.read_file(self.workspace_path, path)
                return {"path": path, "content": content}

            elif tool_name == "list_files":
                directory = args.get("directory", ".")
                files = WorkspaceManager.list_files(self.workspace_path, directory)
                return {"files": files}

            elif tool_name == "get_file_metadata":
                path = args.get("path")
                if not path:
                    return {"error": "Missing required argument 'path'"}
                meta = WorkspaceManager.get_file_metadata(self.workspace_path, path)
                return meta

            elif tool_name == "apply_patch":
                path = args.get("path")
                patch = args.get("patch")
                if not path or not patch:
                    return {"error": "Both 'path' and 'patch' are required"}

                orig = WorkspaceManager.read_file(self.workspace_path, path)
                new_text, stats = apply_patch_to_text(orig, patch, filename=path)
                WorkspaceManager.write_file(self.workspace_path, path, new_text)

                return {
                    "success": True,
                    "path": path,
                    "diff": stats["diff"],
                    "lines_added": stats["lines_added"],
                    "lines_removed": stats["lines_removed"],
                    "message": f"Successfully applied patch to {path}",
                }

            elif tool_name == "write_file":
                path = args.get("path")
                content = args.get("content")
                if not path or content is None:
                    return {"error": "Both 'path' and 'content' are required"}

                # Check if file has test in name - prevent Coder from tampering with tests
                if "test_" in path or "_test" in path:
                    return {"error": "Modifying test files is restricted to prevent invalidating test criteria."}

                WorkspaceManager.write_file(self.workspace_path, path, content)
                return {"success": True, "path": path, "message": f"File {path} written successfully"}

            elif tool_name == "get_diff":
                diff = WorkspaceManager.get_diff(self.workspace_path)
                return {"diff": diff or "No changes detected"}

            elif tool_name == "run_target_test":
                test_path = args.get("test_path") or self.target_test_spec
                # Parse test file and test name if separated by ::
                if "::" in test_path:
                    tf, tt = test_path.split("::", 1)
                else:
                    tf, tt = test_path, None

                res: TestResult = self.sandbox.execute_test(
                    workspace_path=self.workspace_path,
                    test_file=tf,
                    target_test=tt,
                )
                res_dict = res.model_dump()
                self.latest_test_results["target"] = res_dict
                return res_dict

            elif tool_name == "run_regression_tests":
                # Run all regression files
                if not self.regression_test_files:
                    # Search workspace for test_regression*.py
                    all_files = WorkspaceManager.list_files(self.workspace_path)
                    self.regression_test_files = [
                        f for f in all_files if ("test_regression" in f or "test_suite" in f) and f.endswith(".py")
                    ]

                if not self.regression_test_files:
                    return {
                        "passed": True,
                        "total": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "message": "No regression test suites configured for this workspace.",
                    }

                # Run each regression test file
                total = 0
                passed_tests = 0
                failed_tests = 0
                failed_names = []
                all_stdout = []
                all_stderr = []
                all_passed = True
                duration = 0

                for reg_file in self.regression_test_files:
                    res: TestResult = self.sandbox.execute_test(
                        workspace_path=self.workspace_path,
                        test_file=reg_file,
                    )
                    duration += res.duration_ms
                    total += res.total
                    passed_tests += res.passed_tests
                    failed_tests += res.failed_tests
                    failed_names.extend(res.failed_test_names)
                    if not res.passed:
                        all_passed = False
                    all_stdout.append(f"=== {reg_file} ===\n{res.stdout}")
                    if res.stderr:
                        all_stderr.append(f"=== {reg_file} ===\n{res.stderr}")

                reg_dict = {
                    "passed": all_passed,
                    "total": total,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "failed_names": failed_names,
                    "duration_ms": duration,
                    "stdout": "\n".join(all_stdout),
                    "stderr": "\n".join(all_stderr),
                    "failure_type": "NONE" if all_passed else "REGRESSION",
                }
                self.latest_test_results["regression"] = reg_dict
                return reg_dict

            elif tool_name == "create_checkpoint":
                ckpt_id = WorkspaceManager.create_checkpoint(self.workspace_path, "Agent Checkpoint")
                return {"checkpoint_id": ckpt_id, "status": "Checkpoint created"}

            elif tool_name == "rollback":
                ckpt_id = args.get("checkpoint_id")
                if not ckpt_id:
                    return {"error": "Missing 'checkpoint_id'"}
                ok = WorkspaceManager.rollback(self.workspace_path, ckpt_id)
                return {"success": ok, "checkpoint_id": ckpt_id}

            elif tool_name == "get_test_summary":
                return self.latest_test_results or {"message": "No test runs executed in this attempt yet."}

            else:
                return {"error": f"Unknown tool '{tool_name}'"}

        except SecurityError as sec_err:
            return {"error": f"Security violation: {str(sec_err)}"}
        except PatchError as p_err:
            return {"error": f"Patch error: {str(p_err)}"}
        except FileNotFoundError as fnf_err:
            return {"error": f"File not found: {str(fnf_err)}"}
        except Exception as e:
            logger.exception(f"Unexpected error executing {tool_name}")
            return {"error": f"Internal tool execution error: {str(e)}"}
