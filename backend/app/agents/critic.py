import json
import time
import logging
from typing import Dict, Any
from groq import Groq
from backend.app.config import settings
from backend.app.agents.mock_agent import MockAgent

logger = logging.getLogger("agents.critic")

CRITIC_SYSTEM_PROMPT = """You are an objective, rigorous verification Critic Agent in a Self-Healing Code Repair Pipeline.
Your role is to critically evaluate proposed code repairs using objective test execution results and code diffs.

NON-NEGOTIABLE HARD RULES:
1. If the regression test suite failed, your verdict CANNOT be PASS under any circumstance.
2. If the target test failed, your verdict CANNOT be PASS.
3. You must only issue PASS if BOTH the target test passed AND the regression test suite passed AND the diff is clean.
4. Allowed verdicts: PASS, REVISE, ESCALATE.
5. If the system has reached or exceeded max attempts, use ESCALATE if still failing.
6. Return your evaluation strictly formatted as a valid JSON object with keys:
   - "verdict": "PASS" | "REVISE" | "ESCALATE"
   - "confidence": float between 0.0 and 1.0
   - "root_cause": concise 1-sentence root cause explanation
   - "analysis": concise structured summary explaining why the repair succeeded or failed, and specific corrective guidance for the Coder.
"""


class CriticAgent:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.critic_model
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not instantiate Groq client: {e}")

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the Critic Agent turn, evaluating test evidence and diff."""
        if settings.mock_llm or not self.client:
            logger.info("Running Critic in mock mode")
            return MockAgent.get_critic_response(state)

        target_res = state.get("target_test_result", {})
        reg_res = state.get("regression_result", {})
        attempt = state.get("attempt", 1)
        max_attempts = state.get("max_attempts", 3)
        diff = state.get("current_diff", "")
        source_file = state.get("source_file", "")
        original_code = state.get("original_code", "")
        current_code = state.get("current_code", "")
        coder_plan = state.get("coder_plan", "")

        target_passed = target_res.get("passed", False)
        reg_passed = reg_res.get("passed", False)

        # Pre-check hard rules deterministically
        if not target_passed or not reg_passed:
            deterministic_verdict = "ESCALATE" if attempt >= max_attempts else "REVISE"
        else:
            deterministic_verdict = "PASS"

        prompt = f"""EVALUATION REQUEST (Attempt {attempt} of {max_attempts}):
Source File: {source_file}
Coder's Stated Plan: {coder_plan[:400]}

OBJECTIVE EXECUTION EVIDENCE:
Target Test Passed: {target_passed}
Target Test Details:
{json.dumps(target_res, indent=2)[:600]}

Regression Suite Passed: {reg_passed}
Regression Suite Details:
{json.dumps(reg_res, indent=2)[:600]}

APPLIED CODE DIFF:
```diff
{diff[:1200] if diff else "No diff"}
```

REMINDER: If regression passed is False, verdict CANNOT be PASS.
Evaluate this repair and respond with valid JSON containing:
{{
  "verdict": "{deterministic_verdict}",
  "confidence": 0.95,
  "root_cause": "concise explanation",
  "analysis": "detailed critique and recommendation"
}}
"""

        messages = [
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Call Groq with exponential backoff
        for delay in [1, 2, 4]:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)

                # ENFORCE HARD RULE POST-PROCESSING
                verdict = data.get("verdict", deterministic_verdict).upper()
                if (not target_passed or not reg_passed) and verdict == "PASS":
                    logger.warning("Overriding LLM Critic verdict: regressions or target failures cannot PASS")
                    verdict = deterministic_verdict

                if attempt >= max_attempts and verdict == "REVISE":
                    verdict = "ESCALATE"

                usage = {
                    "input": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                    "output": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
                }

                return {
                    "verdict": verdict,
                    "confidence": float(data.get("confidence", 0.9)),
                    "root_cause": data.get("root_cause", "Issue in implementation"),
                    "analysis": data.get("analysis", "Review complete"),
                    "tokens": usage,
                }
            except Exception as e:
                logger.warning(f"Critic Groq call attempt failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)

        # Fallback to MockAgent
        logger.error("Critic Groq call failed; falling back to MockAgent")
        return MockAgent.get_critic_response(state)
