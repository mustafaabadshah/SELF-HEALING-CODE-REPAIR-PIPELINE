from typing import TypedDict, List, Dict, Any, Optional


class AttemptRecord(TypedDict):
    attempt: int
    hypothesis: str
    coder_plan: str
    diff: str
    target_test_passed: bool
    regression_passed: bool
    critic_verdict: str
    critic_analysis: str
    failure_type: str
    timestamp: str
    latency_ms: int
    input_tokens: int
    output_tokens: int


class RepairState(TypedDict):
    task_id: str
    workspace_id: str
    workspace_path: str

    source_file: str
    test_file: str
    target_test: str
    regression_files: List[str]

    original_code: str
    current_code: str
    current_diff: str

    coder_plan: str
    coder_summary: str

    target_test_result: Dict[str, Any]
    regression_result: Dict[str, Any]

    critic_analysis: str
    critic_verdict: str  # "PASS", "REVISE", "ESCALATE"
    critic_confidence: Optional[float]

    attempt: int
    max_attempts: int

    failure_type: str
    root_cause: str

    attempts: List[Dict[str, Any]]
    errors: List[str]

    workspace_checkpoint_id: Optional[str]

    status: str  # QUEUED, RUNNING, SELF_CORRECTING, SUCCESS, FAILED, HUMAN_REVIEW

    trace_id: str
    trace_url: Optional[str]

    # Conversation history & native tool calling buffers
    messages: List[Dict[str, Any]]
    pending_tool_calls: List[Dict[str, Any]]
    tool_round: int
    max_tool_rounds: int
