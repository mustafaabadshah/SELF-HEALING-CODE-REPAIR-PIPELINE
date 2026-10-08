import json
import time
from pathlib import Path
from typing import Optional
from backend.app.sandbox.base import BaseSandbox, TestResult

try:
    import docker
    from docker.errors import DockerException
except ImportError:
    docker = None
    DockerException = Exception


class DockerSandbox(BaseSandbox):
    """
    Docker container sandbox implementation.
    Executes tests inside an unprivileged Docker container with resource limits,
    no network access, and strict timeouts.
    """

    IMAGE_NAME = "self-healing-repair-sandbox:latest"

    def __init__(self):
        self.client = None
        if docker:
            try:
                self.client = docker.from_env()
                self.client.ping()
            except Exception:
                self.client = None

    def is_available(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def execute_test(
        self,
        workspace_path: str,
        test_file: str,
        target_test: Optional[str] = None,
        timeout_seconds: int = 30,
    ) -> TestResult:
        start_time = time.time()
        if not self.is_available():
            return TestResult(
                passed=False,
                exit_code=1,
                duration_ms=0,
                failure_type="INFRASTRUCTURE_ERROR",
                stderr="Docker daemon is not responsive or not installed",
                error_summary="Docker unavailable",
            )

        ws_abs = str(Path(workspace_path).resolve())
        cmd = ["/workspace", test_file]
        if target_test:
            cmd.append(target_test)

        try:
            # Run container
            container = self.client.containers.run(
                image=self.IMAGE_NAME,
                command=cmd,
                volumes={ws_abs: {"bind": "/workspace", "mode": "rw"}},
                network_mode="none",
                mem_limit="512m",
                nano_cpus=1_000_000_000,
                user="sandboxuser",
                detach=True,
                remove=False,
            )

            # Wait with timeout
            try:
                res = container.wait(timeout=timeout_seconds)
                exit_code = res.get("StatusCode", 0)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            except Exception as wait_err:
                container.kill()
                container.remove(v=True, force=True)
                duration_ms = int((time.time() - start_time) * 1000)
                return TestResult(
                    passed=False,
                    exit_code=124,
                    duration_ms=duration_ms,
                    failure_type="TIMEOUT",
                    stderr=f"Container execution timed out after {timeout_seconds}s: {wait_err}",
                    error_summary="Execution timed out in Docker container",
                )
            finally:
                try:
                    container.remove(v=True, force=True)
                except Exception:
                    pass

            duration_ms = int((time.time() - start_time) * 1000)

            # Parse JSON output from runner if present
            try:
                # runner outputs JSON
                data = json.loads(logs.strip())
                return TestResult(**data)
            except Exception:
                # Fallback to standard parsing
                passed = (exit_code == 0)
                return TestResult(
                    passed=passed,
                    exit_code=exit_code,
                    duration_ms=duration_ms,
                    stdout=logs,
                    stderr="",
                    total=1,
                    passed_tests=1 if passed else 0,
                    failed_tests=0 if passed else 1,
                    failure_type="NONE" if passed else "TEST_FAILURE",
                )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return TestResult(
                passed=False,
                exit_code=1,
                duration_ms=duration_ms,
                failure_type="INFRASTRUCTURE_ERROR",
                stderr=str(e),
                error_summary=f"Docker container run failed: {str(e)}",
            )
