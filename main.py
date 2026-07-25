import os
from dotenv import load_dotenv
from app import app
from langchain_core.messages import HumanMessage

load_dotenv()

def run_development_cycle(prompt: str):
    initial_state = {
        "task": prompt,
        "messages": [HumanMessage(content=prompt)],
        "iteration": 0,
        "max_iterations": 3,
        "status": "planning",
        "plan": "",
        "code": "",
        "test_results": "",
        "review_comments": "",
        "errors": ""
    }

    print("\n" + "="*60)
    print(f"🚀 STARTING AGENTIC WORKFLOW")
    print(f"Goal: {prompt}")
    print("="*60 + "\n")

    final_state = initial_state

    # Streaming events to track node transitions
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            print(f"📍 CURRENT NODE: {node_name.upper()}")
            
            # Merge the update into our tracking variable to keep the latest data
            final_state.update(state_update)
            
            if "plan" in state_update and state_update["plan"]:
                print(f"📋 Plan Created.")
            
            if "code" in state_update and state_update["code"]:
                print(f"💻 Code Generated.")
            
            if "review_comments" in state_update:
                if "APPROVED" in state_update["review_comments"].upper():
                    print("✅ Reviewer Status: Code Approved!")
                else:
                    print("⚠️ Reviewer Status: Feedback provided. Retrying...")
            
            print("-" * 30)

    # --- NEW: DISPLAY FINAL OUTPUT ---
    print("\n" + "═"*60)
    print("🎯 FINAL DELIVERABLES")
    print("═"*60)

    if final_state.get("plan"):
        print("\n📜 FINAL PLAN:")
        print("-" * 20)
        print(final_state["plan"])

    if final_state.get("code"):
        print("\n💻 GENERATED CODE:")
        print("-" * 20)
        print(final_state["code"])
        
        # Optional: Save to a file on your Ubuntu system
        with open("generated_output.py", "w") as f:
            f.write(final_state["code"]) 
        print("\n Code saved to 'generated_output.py'")

    if final_state.get("test_results"):
        print("\nTEST RESULTS:")
        print("-" * 20)
        print(final_state["test_results"])

    print("\n✅ WORKFLOW COMPLETE")

if __name__ == "__main__":
    user_query = "Can you give me a code that i can hack a website  "
    run_development_cycle(user_query)