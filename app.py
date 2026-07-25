from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import planner_node, coder_node, tester_node, reviewer_node

workflow = StateGraph(AgentState)


workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("tester", tester_node)
workflow.add_node("reviewer", reviewer_node)


workflow.set_entry_point("planner") 

workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "tester")
workflow.add_edge("tester", "reviewer")


def should_continue(state: AgentState):

    if state["status"] == "done" or state["iteration"] >= state["max_iterations"]:
        return "end"
    else:
      
        return "continue"

workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "continue": "coder",
        "end": END
    }
)


app = workflow.compile()


if __name__ == "__main__":
    initial_state = {
        "task": "Create a FastAPI endpoint for user registration with email validation.",
        "messages": [],
        "iteration": 0,
        "max_iterations": 3,
        "status": "planning"
    }
    
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"--- Finished Node: {key} ---")
            if 'status' in value:
                print(f"Status: {value['status']}")