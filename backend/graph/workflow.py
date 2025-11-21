from langgraph.graph import StateGraph, END
from backend.graph.state import AuditState
from backend.graph.nodes import scanner_node, critic_node, fixer_node

def create_audit_graph():
    """
    Constructs the LangGraph workflow for the Accessibility Audit.
    """
    # 1. Initialize the Graph with our State schema
    workflow = StateGraph(AuditState)

    # 2. Add the Nodes (The Workers)
    workflow.add_node("scanner", scanner_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("fixer", fixer_node)

    # 3. Define the Edges (The Logic Flow)
    # Start -> Scanner -> Critic -> Fixer -> End
    workflow.set_entry_point("scanner")
    
    workflow.add_edge("scanner", "critic")
    workflow.add_edge("critic", "fixer")
    workflow.add_edge("fixer", END)

    # 4. Compile the Graph (Turn it into a runnable application)
    return workflow.compile()

# Create a singleton instance to be imported by the API
audit_graph = create_audit_graph()