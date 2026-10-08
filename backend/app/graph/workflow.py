from langgraph.graph import StateGraph, START, END
from backend.app.graph.state import RepairState
from backend.app.graph.nodes import (
    initialize_repair_node,
    inspect_workspace_node,
    analyze_failure_node,
    coder_node,
    execute_tool_calls_node,
    target_test_node,
    regression_test_node,
    critic_node,
    route_decision_node,
    rollback_node,
    human_escalation_node,
    finalize_success_node,
    finalize_failure_node,
)
from backend.app.graph.routing import should_continue_tools, route_after_critic


def build_repair_graph():
    """
    Constructs the complete LangGraph StateGraph for the Self-Healing Code Repair Pipeline.
    Implements true collaborative cyclical graph execution with native tools,
    deterministic sandboxed testing, critic evaluation, and human escalation.
    """
    workflow = StateGraph(RepairState)

    # Register Nodes
    workflow.add_node("initialize_repair", initialize_repair_node)
    workflow.add_node("inspect_workspace", inspect_workspace_node)
    workflow.add_node("analyze_failure", analyze_failure_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("execute_tools", execute_tool_calls_node)
    workflow.add_node("target_test", target_test_node)
    workflow.add_node("regression_test", regression_test_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("route_decision", route_decision_node)
    workflow.add_node("rollback", rollback_node)
    workflow.add_node("human_escalation", human_escalation_node)
    workflow.add_node("finalize_success", finalize_success_node)
    workflow.add_node("finalize_failure", finalize_failure_node)

    # Initial flow
    workflow.add_edge(START, "initialize_repair")
    workflow.add_edge("initialize_repair", "inspect_workspace")
    workflow.add_edge("inspect_workspace", "analyze_failure")
    workflow.add_edge("analyze_failure", "coder")

    # Coder to Tools conditional branch
    workflow.add_conditional_edges(
        "coder",
        should_continue_tools,
        {
            "execute_tools": "execute_tools",
            "target_test": "target_test",
        },
    )

    workflow.add_edge("execute_tools", "target_test")
    workflow.add_edge("target_test", "regression_test")
    workflow.add_edge("regression_test", "critic")
    workflow.add_edge("critic", "route_decision")

    # Routing from Critic
    workflow.add_conditional_edges(
        "route_decision",
        route_after_critic,
        {
            "success": "finalize_success",
            "retry": "rollback",
            "human_review": "human_escalation",
        },
    )

    # Retrying loop: rollback increments attempt and routes back to Coder
    workflow.add_edge("rollback", "coder")

    # Terminal nodes
    workflow.add_edge("finalize_success", END)
    workflow.add_edge("human_escalation", END)
    workflow.add_edge("finalize_failure", END)

    return workflow.compile()


repair_graph = build_repair_graph()
