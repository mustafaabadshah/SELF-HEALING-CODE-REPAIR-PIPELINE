import pytest
from backend.app.graph.routing import route_after_critic, should_continue_tools


def test_should_continue_tools():
    state_with_tools = {"pending_tool_calls": [{"id": "1", "function": {"name": "read_file"}}]}
    assert should_continue_tools(state_with_tools) == "execute_tools"

    state_without_tools = {"pending_tool_calls": []}
    assert should_continue_tools(state_without_tools) == "target_test"


def test_route_after_critic_success():
    state = {
        "task_id": "test_1",
        "attempt": 1,
        "max_attempts": 3,
        "critic_verdict": "PASS",
        "target_test_result": {"passed": True},
        "regression_result": {"passed": True},
    }
    assert route_after_critic(state) == "success"


def test_route_after_critic_regression_failure():
    # Target passed but regression failed -> must REVISE (retry)
    state = {
        "task_id": "test_2",
        "attempt": 1,
        "max_attempts": 3,
        "critic_verdict": "REVISE",
        "target_test_result": {"passed": True},
        "regression_result": {"passed": False},
    }
    assert route_after_critic(state) == "retry"


def test_route_after_critic_escalation_on_max_attempts():
    state = {
        "task_id": "test_3",
        "attempt": 3,
        "max_attempts": 3,
        "critic_verdict": "REVISE",
        "target_test_result": {"passed": False},
        "regression_result": {"passed": True},
    }
    assert route_after_critic(state) == "human_review"


def test_route_after_critic_explicit_escalation():
    state = {
        "task_id": "test_4",
        "attempt": 1,
        "max_attempts": 3,
        "critic_verdict": "ESCALATE",
        "target_test_result": {"passed": False},
        "regression_result": {"passed": False},
    }
    assert route_after_critic(state) == "human_review"
