from openai import OpenAI
from config import FreeLLMConfig  


client = OpenAI(
    base_url=FreeLLMConfig.BASE_URL,
    api_key=FreeLLMConfig.OPENROUTER_API_KEY,
    
)

def test_agents():
    print(" Multi-Agent Connection Test")
    
    try:
        print(f"Testing Planner Model ({FreeLLMConfig.PLANNER_MODEL})...")
        
        response = client.chat.completions.create(
            model=FreeLLMConfig.PLANNER_MODEL,
            messages=[
                {"role": "user", "content": " i want to build a multi agent system. can you help me to build it?"
        }
            ]
        )
       
        print("✅ Success!")
        print(f"Response: {response.choices[0].message.content[:50]}...")
        
    except Exception as e:
        # ব্যর্থ হলে এরর দেখাবে
        print("Connection Failed!")
        print(f"Error Details: {str(e)}")

if __name__ == "__main__":
    test_agents()