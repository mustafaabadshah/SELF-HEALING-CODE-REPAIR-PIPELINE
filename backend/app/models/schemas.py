from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RegressionFilePayload(BaseModel):
    filename: str
    content: str


class CreateRepairRequest(BaseModel):
    source_file: str = Field(..., description="Target source filename (e.g. buggy_module.py)")
    source_content: str = Field(..., description="Source code text")
    test_file: str = Field(..., description="Target test filename (e.g. test_target.py)")
    test_content: str = Field(..., description="Target test code text")
    target_test: str = Field(..., description="Target test function name or pytest spec (e.g. test_target.py::test_case)")
    regression_tests: List[RegressionFilePayload] = Field(default_factory=list, description="Optional existing regression test suites")
    max_attempts: int = Field(default=3, ge=1, le=5, description="Maximum autonomous repair attempts")
    use_mock: Optional[bool] = Field(default=None, description="Force mock LLM mode for deterministic testing")


class CreateRepairResponse(BaseModel):
    repair_id: str
    status: str
    message: str


class TestRunSummary(BaseModel):
    id: str
    type: str
    passed: bool
    exit_code: int = 0
    duration_ms: int = 0
    stdout: str = ""
    stderr: str = ""
    failure_type: str = ""
    created_at: Optional[datetime] = None


class AttemptSummary(BaseModel):
    id: str
    attempt_number: int
    hypothesis: str
    diff: str
    target_passed: bool
    regression_passed: bool
    critic_verdict: str
    critic_analysis: str
    critic_confidence: Optional[float] = None
    failure_type: str = ""
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    created_at: datetime
    test_runs: List[TestRunSummary] = Field(default_factory=list)


class RepairDetailResponse(BaseModel):
    id: str
    status: str
    source_file: str
    test_file: str
    target_test: str
    max_attempts: int
    current_attempt: int
    trace_id: str
    trace_url: Optional[str]
    error_message: Optional[str]
    final_diff: Optional[str]
    created_at: datetime
    updated_at: datetime
    attempts: List[AttemptSummary] = Field(default_factory=list)


class DiffResponse(BaseModel):
    repair_id: str
    diff: str
    files_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0


class TraceResponse(BaseModel):
    repair_id: str
    trace_id: str
    trace_url: Optional[str]


class EscalationDecisionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVE_PATCH', 'REJECT_PATCH', or 'RESET'")
    comment: Optional[str] = Field(default="", description="Reviewer feedback")


class DashboardMetrics(BaseModel):
    total_repairs: int = 0
    successful_repairs: int = 0
    failed_repairs: int = 0
    escalations: int = 0
    average_attempts: float = 0.0
    average_repair_time_ms: float = 0.0
    regression_rate: float = 0.0
    total_tokens: int = 0
    average_latency_ms: float = 0.0


class ScanDirectoryRequest(BaseModel):
    directory_path: str = Field(..., description="Local directory path to scan for python and test files")


class ScannedFile(BaseModel):
    filename: str
    content: str
    test_cases: List[str] = Field(default_factory=list)


class ScanDirectoryResponse(BaseModel):
    directory_path: str
    source_files: List[ScannedFile]
    test_files: List[ScannedFile]


class PresetItem(BaseModel):
    id: str
    title: str
    category: str
    badge: str
    description: str
    layman_story: str
    source_file: str
    source_content: str
    test_file: str
    test_content: str
    target_test: str
    regression_tests: List[RegressionFilePayload]
    max_attempts: int = 3

