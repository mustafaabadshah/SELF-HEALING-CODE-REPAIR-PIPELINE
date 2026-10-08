import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
from backend.app.sandbox.base import BaseSandbox, TestResult


class LocalSandbox(BaseSandbox):
    """
    Secure isolated local process sandbox.
    Runs tests in the isolated workspace without exposing host environment secrets
    or arbitrary execution tools.
    """

    def execute_test(
        self,
        workspace_path: str,
        test_file: str,
        target_test: Optional[str] = None,
        timeout_seconds: int = 30,
    ) -> TestResult:
        start_time = time.time()
        ws_path = Path(workspace_path).resolve()

        if not ws_path.exists():
            return TestResult(
                passed=False,
                exit_code=1,
                failure_type="INFRASTRUCTURE_ERROR",
                stderr=f"Workspace path does not exist: {workspace_path}",
                error_summary="Workspace directory not found",
            )

        # Build command: pytest target
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "--tb=short",
        ]

        target_spec = test_file
        if target_test:
            if "::" in target_test:
                target_spec = target_test
            elif "::" in test_file:
                target_spec = test_file
            else:
                target_spec = f"{test_file}::{target_test}"
        cmd.append(target_spec)

        # Sanitize environment: NEVER leak LLM keys or secrets, but preserve Python runtime paths
        safe_env = os.environ.copy()
        for key in list(safe_env.keys()):
            k_upper = key.upper()
            if any(secret in k_upper for secret in ["GROQ", "LANGFUSE", "SECRET", "TOKEN", "KEY", "AUTH", "PASS"]):
                safe_env.pop(key, None)

        existing_pp = safe_env.get("PYTHONPATH", "")
        safe_env["PYTHONPATH"] = f"{ws_path}{os.pathsep}{existing_pp}" if existing_pp else str(ws_path)
        safe_env["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ws_path),
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            duration_ms = int((time.time() - start_time) * 1000)
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode

            passed = (exit_code == 0)

            # Categorize failure type
            failure_type = "NONE" if passed else "TEST_FAILURE"
            error_summary = ""

            if not passed:
                combined = stdout + "\n" + stderr
                if "SyntaxError" in combined:
                    failure_type = "SYNTAX_ERROR"
                    error_summary = "Syntax error in modified source code"
                elif "ImportError" in combined or "ModuleNotFoundError" in combined:
                    failure_type = "IMPORT_ERROR"
                    error_summary = "Import/Module not found error"
                elif "AssertionError" in combined or "assert " in combined:
                    failure_type = "ASSERTION_ERROR"
                    error_summary = "Assertion failed during test execution"
                elif "TypeError" in combined:
                    failure_type = "TYPE_ERROR"
                    error_summary = "Type error encountered"
                elif "IndexError" in combined or "KeyError" in combined:
                    failure_type = "BOUNDARY_ERROR"
                    error_summary = "Boundary / indexing error"
                else:
                    failure_type = "TEST_FAILURE"
                    error_summary = "Test execution failed"

            # Parse test counts
            passed_count = 0
            failed_count = 0
            failed_names = []

            for line in stdout.splitlines():
                line_str = line.strip()
                if " PASSED" in line_str:
                    passed_count += 1
                elif " FAILED" in line_str:
                    failed_count += 1
                    parts = line_str.split()
                    if parts:
                        failed_names.append(parts[0])

            total_count = passed_count + failed_count
            if total_count == 0:
                total_count = 1
                if passed:
                    passed_count = 1
                else:
                    failed_count = 1

            return TestResult(
                passed=passed,
                exit_code=exit_code,
                duration_ms=duration_ms,
                stdout=stdout,
                stderr=stderr,
                total=total_count,
                passed_tests=passed_count,
                failed_tests=failed_count,
                failed_test_names=failed_names,
                failure_type=failure_type,
                error_summary=error_summary,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return TestResult(
                passed=False,
                exit_code=124,
                duration_ms=duration_ms,
                stdout=e.stdout or "" if isinstance(e.stdout, str) else "",
                stderr=e.stderr or "Execution timed out" if isinstance(e.stderr, str) else "Execution timed out",
                total=1,
                passed_tests=0,
                failed_tests=1,
                failed_test_names=[target_spec],
                failure_type="TIMEOUT",
                error_summary=f"Execution exceeded timeout limit ({timeout_seconds}s)",
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return TestResult(
                passed=False,
                exit_code=1,
                duration_ms=duration_ms,
                stdout="",
                stderr=str(e),
                total=1,
                passed_tests=0,
                failed_tests=1,
                failed_test_names=[target_spec],
                failure_type="INFRASTRUCTURE_ERROR",
                error_summary=f"Failed to execute test runner: {str(e)}",
            )
