
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    
    messages: Annotated[list, add_messages]
    
    task: str              
    plan: str            
    code: str             
    test_results: str      
    review_comments: str   
    errors: str           
    
    iteration: int         
    max_iterations: int    
    status: str           
    final_output: str     