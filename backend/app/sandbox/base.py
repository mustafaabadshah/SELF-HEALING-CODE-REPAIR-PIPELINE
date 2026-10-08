from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field


class TestResult(BaseModel):
    passed: bool
    exit_code: int = 0
    duration_ms: int = 0
    stdout: str = ""
    stderr: str = ""
    total: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    failed_test_names: List[str] = Field(default_factory=list)
    failure_type: str = "NONE"  # NONE, ASSERTION_ERROR, SYNTAX_ERROR, IMPORT_ERROR, TIMEOUT, INFRASTRUCTURE_ERROR, TEST_FAILURE
    error_summary: str = ""


class BaseSandbox(ABC):
    @abstractmethod
    def execute_test(
        self,
        workspace_path: str,
        test_file: str,
        target_test: Optional[str] = None,
        timeout_seconds: int = 30,
    ) -> TestResult:
        """Executes a target or regression test in the isolated sandbox."""
        pass
