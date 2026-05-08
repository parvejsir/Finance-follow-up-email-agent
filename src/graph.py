from langgraph.graph import StateGraph, END
from typing import TypedDict
from src.nodes import router_node, generation_node, send_email_node, escalation_node

class AgentState(TypedDict):
    invoice_no: str
    client_name: str
    amount: float
    due_date: str
    contact_email: str
    follow_up_count: int
    email_body: str
    next_action: str
    status: str

def build_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("generator", generation_node)
    workflow.add_node("sender", send_email_node)
    workflow.add_node("escalator", escalation_node)

    # Define Edges
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next_action"],
        {
            "generate_email": "generator",
            "escalate": "escalator"
        }
    )
    
    workflow.add_edge("generator", "sender")
    workflow.add_edge("sender", END)
    workflow.add_edge("escalator", END)

    return workflow.compile()