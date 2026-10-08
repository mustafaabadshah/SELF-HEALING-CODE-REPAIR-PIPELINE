import json
from typing import Dict, Any, List


class MockAgent:
    """
    Deterministic mock agent for testing and mock mode (MOCK_LLM=true).
    Guarantees the exact required self-healing demonstration:
    - Attempt 1: Plausible patch that fixes target test but breaks existing regression suite.
    - Critic Attempt 1: REVISE (identifies regression and contract violation).
    - Attempt 2: Corrected patch that fixes both target and regression tests.
    - Critic Attempt 2: PASS (approves solution).
    """

    @staticmethod
    def get_coder_response(state: Dict[str, Any]) -> Dict[str, Any]:
        attempt = state.get("attempt", 1)
        source_file = state.get("source_file", "buggy_module.py")

        if attempt == 1:
            hypothesis = (
                "The discount function fails on string inputs like '20%'. "
                "I will convert any string by stripping '%' and dividing by 100, and also divide any number by 100."
            )
            # This naive patch solves target test ('20%') but breaks decimal discounts (0.15) in regression tests!
            patch = (
                "<<<<<<< SEARCH\n"
                "def calculate_discounted_price(price: float, discount) -> float:\n"
                "    if price < 0:\n"
                "        raise ValueError(\"Price cannot be negative\")\n"
                "    # Buggy baseline: assumes discount is numeric decimal only, fails on string '20%'\n"
                "    return round(price * (1.0 - discount), 2)\n"
                "=======\n"
                "def calculate_discounted_price(price: float, discount) -> float:\n"
                "    if price < 0:\n"
                "        raise ValueError(\"Price cannot be negative\")\n"
                "    # Attempt 1 naive fix: treats all discounts as percentages out of 100\n"
                "    if isinstance(discount, str) and discount.endswith('%'):\n"
                "        d = float(discount.rstrip('%')) / 100.0\n"
                "    else:\n"
                "        # Naive bug: divides decimal discounts (0.15) by 100 again, breaking callers!\n"
                "        d = float(discount) / 100.0\n"
                "    return round(price * (1.0 - d), 2)\n"
                ">>>>>>> REPLACE"
            )
            return {
                "hypothesis": hypothesis,
                "plan": "Normalize percentage strings by stripping '%' and dividing by 100.",
                "tool_calls": [
                    {
                        "id": "mock_call_1",
                        "type": "function",
                        "function": {
                            "name": "apply_patch",
                            "arguments": json.dumps({"path": source_file, "patch": patch}),
                        },
                    }
                ],
                "tokens": {"input": 450, "output": 120},
            }

        else:
            # Attempt 2: Learns from Critic feedback!
            hypothesis = (
                "In Attempt 1, dividing all non-string discounts by 100 broke decimal discount values (e.g. 0.15) "
                "in regression tests. I will properly inspect the value: "
                "if string with '%', divide by 100; if numeric <= 1.0, treat as decimal fraction; otherwise divide by 100."
            )
            patch = (
                "<<<<<<< SEARCH\n"
                "def calculate_discounted_price(price: float, discount) -> float:\n"
                "    if price < 0:\n"
                "        raise ValueError(\"Price cannot be negative\")\n"
                "    # Buggy baseline: assumes discount is numeric decimal only, fails on string '20%'\n"
                "    return round(price * (1.0 - discount), 2)\n"
                "=======\n"
                "def calculate_discounted_price(price: float, discount) -> float:\n"
                "    if price < 0:\n"
                "        raise ValueError(\"Price cannot be negative\")\n"
                "    # Attempt 2 corrected fix: differentiates between percentage strings, decimals, and numbers\n"
                "    if isinstance(discount, str):\n"
                "        d = float(discount.strip().rstrip('%')) / 100.0\n"
                "    elif isinstance(discount, (int, float)):\n"
                "        d = float(discount) / 100.0 if discount > 1.0 else float(discount)\n"
                "    else:\n"
                "        raise ValueError(f'Invalid discount format: {discount}')\n"
                "    return round(price * (1.0 - d), 2)\n"
                ">>>>>>> REPLACE"
            )
            return {
                "hypothesis": hypothesis,
                "plan": "Robustly normalize discount rates handling string %, decimal fraction <= 1.0, and whole numbers.",
                "tool_calls": [
                    {
                        "id": "mock_call_2",
                        "type": "function",
                        "function": {
                            "name": "apply_patch",
                            "arguments": json.dumps({"path": source_file, "patch": patch}),
                        },
                    }
                ],
                "tokens": {"input": 580, "output": 160},
            }

    @staticmethod
    def get_critic_response(state: Dict[str, Any]) -> Dict[str, Any]:
        target_res = state.get("target_test_result", {})
        reg_res = state.get("regression_result", {})
        attempt = state.get("attempt", 1)

        target_passed = target_res.get("passed", False)
        reg_passed = reg_res.get("passed", False)

        if not target_passed or not reg_passed:
            verdict = "REVISE"
            if attempt >= state.get("max_attempts", 3):
                verdict = "ESCALATE"

            analysis = (
                "CRITIC VERIFICATION REPORT:\n"
                f"1. Target Test: {'PASS' if target_passed else 'FAIL'}\n"
                f"2. Regression Suite: {'PASS' if reg_passed else 'FAIL'}\n"
                "Root Cause: The proposed patch solves the target percentage string issue, "
                "but introduced a REGRESSION by dividing existing decimal discounts (e.g. 0.15) by 100 again. "
                "Existing callers expect values <= 1.0 to remain as direct fractions.\n"
                "Recommendation: Differentiate between decimal rates (<= 1.0) and whole percentage numbers."
            )
            return {
                "verdict": verdict,
                "confidence": 0.95,
                "root_cause": "Unconditional division by 100 violates existing decimal discount API contract",
                "analysis": analysis,
                "tokens": {"input": 620, "output": 140},
            }
        else:
            return {
                "verdict": "PASS",
                "confidence": 0.99,
                "root_cause": "Fixed: Both string percentages and existing numeric/decimal discounts handled cleanly",
                "analysis": (
                    "CRITIC VERIFICATION REPORT:\n"
                    "1. Target Test: PASS\n"
                    "2. Regression Suite: PASS (All tests passed)\n"
                    "3. Diff Analysis: Implementation is minimal, preserves API contract, and correctly normalizes inputs.\n"
                    "Verdict: PASS"
                ),
                "tokens": {"input": 700, "output": 110},
            }
