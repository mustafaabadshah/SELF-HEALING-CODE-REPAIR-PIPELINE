import json
import time
import logging
from typing import Dict, Any, List
from groq import Groq
from backend.app.config import settings
from backend.app.tools.schemas import TOOL_DEFINITIONS
from backend.app.agents.mock_agent import MockAgent

logger = logging.getLogger("agents.coder")

CODER_SYSTEM_PROMPT = """You are an expert autonomous Python Coder Agent in a Self-Healing Code Repair Pipeline.
Your goal is to diagnose the root cause of a failing test, formulate a minimal safe repair hypothesis, and apply a patch using native tools.

HARD RULES:
1. Make minimal, precise, surgical code changes. Do not rewrite working functions unnecessarily.
2. Preserve existing behavior and API contracts.
3. NEVER modify the test files. Only repair the source code under test.
4. Use native tools (read_file, apply_patch, get_diff, run_target_test, run_regression_tests) to inspect and fix.
5. If previous attempts failed, inspect the Critic's feedback and test errors carefully.
   DO NOT REPEAT PREVIOUS FAILED APPROACHES.
6. The test execution sandbox is the sole authority for correctness.
"""


class CoderAgent:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.coder_model
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not instantiate Groq client: {e}")

    def _format_attempt_history(self, attempts: List[Dict[str, Any]]) -> str:
        if not attempts:
            return "No previous attempts yet. This is Attempt 1."

        lines = ["=== PREVIOUS FAILED ATTEMPTS (SHARED WORKING MEMORY) ==="]
        for att in attempts:
            lines.append(f"\n[Attempt {att.get('attempt')}]")
            lines.append(f"  Hypothesis: {att.get('hypothesis', 'N/A')}")
            lines.append(f"  Target Test: {'PASS' if att.get('target_test_passed') else 'FAIL'}")
            lines.append(f"  Regression Suite: {'PASS' if att.get('regression_passed') else 'FAIL'}")
            lines.append(f"  Critic Verdict: {att.get('critic_verdict', 'N/A')}")
            lines.append(f"  Critic Analysis: {att.get('critic_analysis', 'N/A')}")
            lines.append(f"  Diff Summary: {att.get('diff', '')[:300]}...")
            lines.append("  LESSON: Do NOT repeat this failed approach. Address the Critic's identified failure point!")
        lines.append("\n=======================================================")
        return "\n".join(lines)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the Coder Agent turn, generating hypothesis, plan, and native tool calls."""
        if settings.mock_llm or not self.client:
            logger.info("Running Coder in mock mode")
            return MockAgent.get_coder_response(state)

        source_file = state.get("source_file", "")
        test_file = state.get("test_file", "")
        target_test = state.get("target_test", "")
        current_code = state.get("current_code", "")
        attempt_num = state.get("attempt", 1)
        max_attempts = state.get("max_attempts", 3)
        failure_type = state.get("failure_type", "")
        target_test_result = state.get("target_test_result", {})
        regression_result = state.get("regression_result", {})

        history_text = self._format_attempt_history(state.get("attempts", []))

        prompt = f"""Repair Task (Attempt {attempt_num} of {max_attempts}):
Source File: {source_file}
Test File: {test_file}
Target Test: {target_test}

Current Failure Classification: {failure_type}

Latest Target Test Result:
{json.dumps(target_test_result, indent=2)[:800]}

Latest Regression Test Result:
{json.dumps(regression_result, indent=2)[:800]}

{history_text}

Current Code of {source_file}:
```python
{current_code}
```

Instructions:
1. Explain your hypothesis and plan for fixing the issue while avoiding past regressions.
2. Invoke `apply_patch` (or other appropriate tools) to fix `{source_file}`.
3. If using `apply_patch`, provide a valid SEARCH/REPLACE block or unified diff.
"""

        messages = [
            {"role": "system", "content": CODER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Call Groq with exponential backoff
        for delay in [1, 2, 4]:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.2,
                )
                msg = response.choices[0].message
                tool_calls = []
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        })

                content = msg.content or ""
                usage = {
                    "input": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                    "output": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
                }

                # Extract hypothesis and plan from content
                hypothesis = content.strip().split("\n")[0] if content else f"Attempt {attempt_num} repair"
                if len(hypothesis) > 300:
                    hypothesis = hypothesis[:297] + "..."

                return {
                    "hypothesis": hypothesis,
                    "plan": content,
                    "tool_calls": tool_calls,
                    "tokens": usage,
                }
            except Exception as e:
                logger.warning(f"Groq API call attempt failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)

        # Fallback to MockAgent if Groq API encounters persistent issues
        logger.error("Groq API calls failed after retries; falling back to MockAgent")
        return MockAgent.get_coder_response(state)
