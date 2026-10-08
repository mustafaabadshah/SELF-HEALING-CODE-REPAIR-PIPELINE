import logging
from typing import Literal
from backend.app.graph.state import RepairState

logger = logging.getLogger("graph.routing")


def should_continue_tools(state: RepairState) -> Literal["execute_tools", "target_test"]:
    """Routes from coder to execute_tools if tool calls were requested, else directly to target_test."""
    tool_calls = state.get("pending_tool_calls", [])
    if tool_calls:
        return "execute_tools"
    return "target_test"


def route_after_critic(state: RepairState) -> Literal["success", "retry", "human_review"]:
    """
    Core deterministic routing logic following Requirement 14 & 15:
    - Target PASS + Regression PASS + Critic PASS -> SUCCESS
    - Regression FAIL or Target FAIL -> REVISE (retry with incremented attempt)
    - Max attempts reached -> HUMAN_REVIEW
    """
    task_id = state.get("task_id", "")
    attempt = state.get("attempt", 1)
    max_attempts = state.get("max_attempts", 3)
    critic_verdict = state.get("critic_verdict", "REVISE")

    target_res = state.get("target_test_result", {})
    reg_res = state.get("regression_result", {})

    target_passed = bool(target_res.get("passed", False))
    reg_passed = bool(reg_res.get("passed", False))

    logger.info(
        f"[{task_id}] Routing Check - Attempt {attempt}/{max_attempts}: "
        f"Target={target_passed}, Regression={reg_passed}, Critic={critic_verdict}"
    )

    # SUCCESS condition: all three must be True
    if critic_verdict == "PASS" and target_passed and reg_passed:
        logger.info(f"[{task_id}] -> ROUTE: success")
        return "success"

    # ESCALATION condition: reached limit or critic explicitly escalated
    if attempt >= max_attempts or critic_verdict == "ESCALATE":
        logger.info(f"[{task_id}] -> ROUTE: human_review (attempts={attempt}/{max_attempts})")
        return "human_review"

    # RETRY condition: self-healing loop
    logger.info(f"[{task_id}] -> ROUTE: retry (attempt {attempt} -> {attempt + 1})")
    return "retry"
