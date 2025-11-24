from langgraph.graph import StateGraph, END
from backend.graph.state import AuditState
from backend.graph.nodes import scanner_node, critic_node, fixer_node, vision_analyzer_node

def create_audit_graph():
    workflow = StateGraph(AuditState)

    # Add Nodes
    workflow.add_node("scanner", scanner_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("vision", vision_analyzer_node)
    workflow.add_node("fixer", fixer_node)

    # Define Edges
    workflow.set_entry_point("scanner")
    workflow.add_edge("scanner", "critic")
    workflow.add_edge("critic", "vision")
    workflow.add_edge("vision", "fixer")
    workflow.add_edge("fixer", END)

    return workflow.compile()

audit_graph = create_audit_graph()