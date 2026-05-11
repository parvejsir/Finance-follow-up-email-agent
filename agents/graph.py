from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import (
    router_agent, 
    email_generator_agent, 
    validator_agent, 
    sender_agent, 
    escalation_agent
)

def build_v2_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_agent)
    workflow.add_node("generator", email_generator_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("sender", sender_agent)
    workflow.add_node("escalator", escalation_agent)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        lambda x: x["next_node"],
        {
            "generate": "generator",
            "escalate": "escalator"
        }
    )

    workflow.add_edge("generator", "validator")
    
    # CRITICAL FIX: Only go to sender if processing_mode is 'Auto-Process'
    workflow.add_conditional_edges(
        "validator",
        lambda x: "sender" if x.get("processing_mode") == "Auto-Process" else "end_path",
        {
            "sender": "sender",
            "end_path": END,     # Stops here so you can review in UI
            "generate": "generator" 
        }
    )

    workflow.add_edge("sender", END)
    workflow.add_edge("escalator", END)

    return workflow.compile()