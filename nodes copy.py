import os
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
# নতুন ইম্পোর্ট: Gemini মডেলের জন্য
# আগের লাইনটি কমেন্ট বা ডিলিট করে এটি বসান
from langchain_google_genai.chat_models import ChatGoogleGenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import FreeLLMConfig
from state import AgentState

def get_model(model_name: str):
    """
    Logic to route between Gemini, Hugging Face, and OpenRouter.
    """
    # ১. যদি মডেলটি জেমিনি সিরিজের হয় (যেমন: gemini-2.5-flash)
    if "gemini" in model_name.lower():
        return ChatGoogleGenAI(
            model=model_name,
            google_api_key=FreeLLMConfig.GEMINI_API_KEY,
            temperature=0.2, # কোড প্ল্যানিংয়ের জন্য লো-টেম্পারেচার ভালো
            # max_output_tokens=4096 # প্রয়োজন হলে আউটপুট টোকেন লিমিট করতে পারেন
        )

    # ২. যদি মডেলটি Hugging Face-এর জন্য নির্দিষ্ট করা হয়
    if model_name == FreeLLMConfig.TESTER_MODEL:
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=FreeLLMConfig.HF_API_KEY,
            task="text-generation",
            timeout=300 
        )
        return ChatHuggingFace(llm=llm)
    
    # ৩. ডিফল্ট হিসেবে অন্য সব মডেল OpenRouter দিয়ে চলবে
    return ChatOpenAI(
        model=model_name,
        openai_api_key=FreeLLMConfig.OPENROUTER_API_KEY,
        base_url=FreeLLMConfig.BASE_URL,
        max_tokens=4000 # আপনার আগের Credit Error (402) এড়াতে এটি ৪০০০ করা হলো
    )

# ১. Planner Node (এখন স্বয়ংক্রিয়ভাবে Gemini মডেল কল করবে যদি PLANNER_MODEL="gemini-..." হয়)
def planner_node(state: AgentState):
    model = get_model(FreeLLMConfig.PLANNER_MODEL)
    system_prompt = "You are an expert Software Architect. Create a detailed step-by-step technical plan."
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['task'])
    ])
    return {"plan": response.content, "status": "coding", "messages": [response]}

# ২. Coder Node (Stays same, uses OpenRouter)
def coder_node(state: AgentState):
    model = get_model(FreeLLMConfig.CODER_MODEL)
    system_prompt = f"You are an expert Programmer. Write code based on this plan: {state['plan']}"
    user_content = state['task']
    if state.get('review_comments'):
        user_content += f"\n\nPlease fix these issues: {state['review_comments']}"
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ])
    return {"code": response.content, "status": "testing", "messages": [response]}

# ৩. Tester Node (Stays same, uses Hugging Face)
def tester_node(state: AgentState):
    model = get_model(FreeLLMConfig.TESTER_MODEL)
    messages = [
        SystemMessage(content="You are a QA Engineer. Write comprehensive tests for the code provided."),
        HumanMessage(content=f"Code to test:\n{state['code']}")
    ]
    response = model.invoke(messages)
    content = response.content if hasattr(response, 'content') else str(response)
    return {
        "test_results": content,
        "status": "reviewing",
        "messages": [HumanMessage(content=content)]
    }

# ৪. Reviewer Node (Stays same, uses OpenRouter)
def reviewer_node(state: AgentState):
    model = get_model(FreeLLMConfig.REVIEWER_MODEL)
    system_prompt = "Review the code and test results. Say 'APPROVED' if perfect."
    input_text = f"Code: {state['code']}\nTest Results: {state['test_results']}"
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=input_text)
    ])
    new_status = "done" if "APPROVED" in response.content.upper() else "coding"
    return {
        "review_comments": response.content,
        "status": new_status,
        "iteration": state.get('iteration', 0) + 1,
        "messages": [response]
    }