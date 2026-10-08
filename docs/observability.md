# Observability Documentation: Langfuse Integration

The **Self-Healing Code Repair Pipeline** features comprehensive observability using **Langfuse**. Every repair run generates a nested trace tree tracking every agent invocation, tool call, test execution, token expenditure, and latency.

---

## 1. Trace Hierarchy

Every repair request starts a root trace:
`trace_id = repair_{id}`

Nested spans and generations under the root trace:

```text
repair_ABC123 (Root Trace)
├── initialize_repair [Span]
├── inspect_workspace [Span]
├── analyze_failure [Span]
│   └── run_target_test [Span: Baseline failure detection]
├── coder_attempt_1 [Generation: LLM call to Coder Model]
│   ├── tool_read_file [Tool Call]
│   └── tool_apply_patch [Tool Call]
├── target_test [Span: Sandboxed pytest target run]
├── regression_suite [Span: Sandboxed pytest regression run]
├── critic_attempt_1 [Generation: LLM call to Critic Model]
│   └── verdict: REVISE [Span Metadata]
├── rollback [Span: Git checkpoint restore]
├── coder_attempt_2 [Generation: Revised repair based on Critic feedback]
│   └── tool_apply_patch [Tool Call]
├── target_test [Span: Sandboxed pytest target run: PASS]
├── regression_suite [Span: Sandboxed pytest regression run: PASS]
├── critic_attempt_2 [Generation: Critic Model: PASS]
└── finalize_success [Span: Outcome: SUCCESS]
```

---

## 2. Tracked Metrics

For each observation, the pipeline records:
1. **Model Identifiers**: e.g. `openai/gpt-oss-120b`, `openai/gpt-oss-20b`.
2. **Prompts & Completions**: Structured inputs and responses.
3. **Token Usage**: `prompt_tokens`, `completion_tokens`, `total_tokens`.
4. **Execution Latencies**: Agent call latency vs sandbox test execution latency.
5. **Attempt Index**: Correlation of attempts across the multi-turn session.
6. **Verdict & Outcomes**: `PASS`, `REVISE`, `ESCALATE`.

---

## 3. Graceful Degradation Guarantee

When Langfuse is disabled or keys are omitted (`LANGFUSE_ENABLED=false`), the system gracefully no-ops without any performance impact or exceptions.
