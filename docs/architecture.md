# Architecture Documentation: Self-Healing Code Repair Pipeline

The **Self-Healing Code Repair Pipeline** is an autonomous, stateful, collaborative multi-agent system designed for automated software repair with deterministic verification, sandboxed execution, regression prevention, and human review escalation.

Unlike naive linear agent loops or chatbot wrappers, this architecture establishes that **the execution environment and objective test outcomes are the sole authorities of truth**.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    User([User / Developer]) --> Frontend[React Frontend: Vite + Tailwind]
    Frontend -->|REST / WebSocket| API[FastAPI Backend Engine]
    API --> Graph[LangGraph StateGraph Engine]

    subgraph "Stateful Collaborative Agent Loop"
        Graph --> Init[1. initialize_repair]
        Init --> Inspect[2. inspect_workspace]
        Inspect --> Analyze[3. analyze_failure]
        Analyze --> Coder[4. Coder Agent]

        Coder -->|Native Tool Calls| Tools[5. Tool Layer: apply_patch, read_file]
        Coder -->|No Calls / Finished| TargetTest[6. Sandbox: Target Test]
        Tools --> TargetTest

        TargetTest --> RegTest[7. Sandbox: Regression Suite]
        RegTest --> Critic[8. Critic Agent: Impartial Reviewer]
        Critic --> Router{9. Route Decision}

        Router -->|PASS & No Regressions| Success[Finalize Success]
        Router -->|FAIL / Regression & Attempts < Max| Rollback[Rollback & Retry]
        Router -->|Attempts >= Max OR Escalate| Escalate[Human Escalation]

        Rollback -->|Increment Attempt + Shared Memory| Coder
    end

    subgraph "Deterministic Sandboxed Execution"
        TargetTest --> Sandbox[Docker / Isolated Local Sandbox]
        RegTest --> Sandbox
        Sandbox --> Pytest[pytest Test Runner]
    end

    subgraph "Observability Layer"
        Graph -.-> Langfuse[(Langfuse Telemetry)]
        Coder -.-> Langfuse
        Critic -.-> Langfuse
        Sandbox -.-> Langfuse
    end

    Success --> End([Repaired Codebase])
    Escalate --> HumanUI([Human Review UI: Approve / Reject / Reset])
```

---

## 2. LangGraph State Machine & State Transitions

The execution is governed by a strongly typed `RepairState` TypedDict executed across explicit graph nodes:

```mermaid
stateDiagram-v2
    [*] --> initialize_repair
    initialize_repair --> inspect_workspace
    inspect_workspace --> analyze_failure
    analyze_failure --> coder
    coder --> execute_tools: Pending tool calls
    coder --> target_test: No tool calls
    execute_tools --> target_test
    target_test --> regression_test
    regression_test --> critic
    critic --> route_decision
    
    route_decision --> finalize_success: Target PASS + Regression PASS + Critic PASS
    route_decision --> rollback: Target FAIL or Regression FAIL (Attempts < Max)
    route_decision --> human_escalation: Attempts >= Max OR Critic ESCALATE
    
    rollback --> coder: Re-enter with previous attempt history in shared memory
    finalize_success --> [*]
    human_escalation --> [*]
```

---

## 3. Shared Working Memory Schema

State is maintained globally across all agents:

```python
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

    status: str

    trace_id: str
    trace_url: Optional[str]
```

### Attempt History Schema

Every cycle writes an immutable audit record injected into subsequent Coder prompts:
- Attempt Number
- Hypothesis & Plan
- Applied Diff
- Target Test Result (`PASS` / `FAIL`)
- Regression Suite Result (`PASS` / `FAIL`)
- Critic Verdict (`PASS`, `REVISE`, `ESCALATE`)
- Critic Root Cause & Actionable Feedback
- Execution Latency & Token Usage

---

## 4. Multi-Agent Collaboration Roles

### Coder Agent
- **Responsibilities**: Formulates repair hypotheses, writes minimal patches, preserves existing API contracts, reads files.
- **Constraints**: Never modifies test suites, cannot self-certify success, must heed Critic guidance.

### Critic Agent
- **Responsibilities**: Impartial verification based purely on objective execution output and code diffs.
- **Hard Rule**: Under no circumstances can the Critic verdict be `PASS` if regression tests fail.
- **Allowed Verdicts**: `PASS`, `REVISE`, `ESCALATE`.
