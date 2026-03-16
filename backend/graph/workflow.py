# backend/graph/workflow.py

from langgraph.graph import StateGraph, END
from backend.graph.state import AuditState

# Import ALL nodes (including the new ones)
from backend.graph.nodes import (
    scanner_node, 
    critic_node, 
    fixer_node, 
    vision_analyzer_node,
    semantic_node,
    interaction_node,
    input_guard_node  # New
)

def create_audit_graph():
    workflow = StateGraph(AuditState)

    # 1. Add Nodes
    workflow.add_node("input_guard", input_guard_node) # New
    workflow.add_node("scanner", scanner_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("semantic", semantic_node)
    workflow.add_node("interaction", interaction_node)
    workflow.add_node("vision", vision_analyzer_node)
    workflow.add_node("fixer", fixer_node)

    # 2. Define Edges (The Flow)
    workflow.set_entry_point("input_guard")
    
    # Connect them in a chain:
    # Input Guard -> Scanner -> Critic -> Semantic -> Interaction -> Vision -> Fixer -> END
    workflow.add_edge("input_guard", "scanner")
    workflow.add_edge("scanner", "critic")
    workflow.add_edge("critic", "semantic")
    workflow.add_edge("semantic", "interaction")
    workflow.add_edge("interaction", "vision")
    workflow.add_edge("vision", "fixer")
    workflow.add_edge("fixer", END)

    return workflow.compile()

# --- CRITICAL: EXPORT THE GRAPH ---
# This is the variable main.py is trying to import
audit_graph = create_audit_graph()