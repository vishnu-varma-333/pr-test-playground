from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import node_analyst, node_writer, node_critic

# Initialize the Graph
workflow = StateGraph(AgentState)

# 1. Add our Nodes
workflow.add_node("analyst", node_analyst)
workflow.add_node("writer", node_writer)
workflow.add_node("critic", node_critic)

# 2. Set the Flow
workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "writer")
workflow.add_edge("writer", "critic")

# 3. Add Logic: Should we loop back or end?
def should_continue(state: AgentState):
    if "PASS" in state["critic_feedback"].upper():
        return END
    # If critic found issues, go back to writer (limit to 3 tries)
    if state.get("revision_count", 0) >= 2:
        return END
    return "writer"

workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "writer": "writer",
        END: END
    }
)

# 4. Compile the Graph
app = workflow.compile()