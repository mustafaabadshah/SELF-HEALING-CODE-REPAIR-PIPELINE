#!/usr/bin/env python3
"""
Sandbox test execution wrapper.
Executes pytest with structured JSON output and captures errors,
timeouts, stdout, and stderr.
"""
import sys
import os
import json
import time
import subprocess
from pathlib import Path


def run_tests(workspace_dir: str, test_file: str, target_test: str = None) -> dict:
    start_time = time.time()
    workspace_path = Path(workspace_dir).resolve()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--tb=short",
    ]

    target_spec = test_file
    if target_test:
        target_spec = f"{test_file}::{target_test}"
    cmd.append(target_spec)

    env = {
        "PYTHONPATH": str(workspace_path),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workspace_path),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode

        passed = (exit_code == 0)

        # Categorize failure
        failure_type = "NONE" if passed else "TEST_FAILURE"
        error_summary = ""

        if not passed:
            combined = stdout + "\n" + stderr
            if "SyntaxError" in combined:
                failure_type = "SYNTAX_ERROR"
                error_summary = "Syntax error in source code or test"
            elif "ImportError" in combined or "ModuleNotFoundError" in combined:
                failure_type = "IMPORT_ERROR"
                error_summary = "Import/Module not found error"
            elif "AssertionError" in combined:
                failure_type = "ASSERTION_ERROR"
                error_summary = "Assertion failed during test execution"
            elif "TypeError" in combined:
                failure_type = "TYPE_ERROR"
                error_summary = "TypeError encountered"
            elif "IndexError" in combined or "KeyError" in combined:
                failure_type = "BOUNDARY_ERROR"
                error_summary = "Index/Key boundary error"
            else:
                failure_type = "TEST_FAILURE"
                error_summary = "Test execution failed"

        # Count passed / failed tests from stdout
        passed_count = 0
        failed_count = 0
        total_count = 0
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
            total_count = 1 if passed else 1
            if passed:
                passed_count = 1
            else:
                failed_count = 1

        return {
            "passed": passed,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "stdout": stdout,
            "stderr": stderr,
            "total": total_count,
            "passed_tests": passed_count,
            "failed_tests": failed_count,
            "failed_test_names": failed_names,
            "failure_type": failure_type,
            "error_summary": error_summary,
        }

    except subprocess.TimeoutExpired as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "passed": False,
            "exit_code": 124,
            "duration_ms": duration_ms,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "Execution timed out",
            "total": 1,
            "passed_tests": 0,
            "failed_tests": 1,
            "failed_test_names": [target_spec],
            "failure_type": "TIMEOUT",
            "error_summary": "Test execution exceeded timeout limit",
        }
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "passed": False,
            "exit_code": 1,
            "duration_ms": duration_ms,
            "stdout": "",
            "stderr": str(e),
            "total": 1,
            "passed_tests": 0,
            "failed_tests": 1,
            "failed_test_names": [target_spec],
            "failure_type": "INFRASTRUCTURE_ERROR",
            "error_summary": f"Infrastructure failure: {str(e)}",
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: run_test.py <workspace_dir> <test_file> [target_test]"}))
        sys.exit(1)

    ws = sys.argv[1]
    tf = sys.argv[2]
    tt = sys.argv[3] if len(sys.argv) > 3 else None

    result = run_tests(ws, tf, tt)
    print(json.dumps(result, indent=2))
