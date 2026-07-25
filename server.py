import os
from flask import Flask, request, Response, json
from flask_cors import CORS
from app import app as langgraph_app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
server = Flask(__name__)
# আপনার লোকাল ফ্রন্টএন্ড যাতে ব্যাকএন্ডে রিকোয়েস্ট পাঠাতে পারে তার জন্য CORS এনাবল করা হলো
CORS(server)

@server.route('/api/ask', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return json.dumps({"error": "Prompt is required"}), 400

    initial_state = {
        "task": prompt,
        "messages": [HumanMessage(content=prompt)],
        "iteration": 0,
        "max_iterations":1,
        "status": "planning",
        "plan": "",
        "code": "",
        "test_results": "", 
        "review_comments": "",
        "errors": ""
    }

    
    def generate_stream():
        try:
            for event in langgraph_app.stream(initial_state):
                for node_name, state_update in event.items():
                    
                    packet = {
                        "node": node_name.upper(),
                        "plan": state_update.get("plan", ""),
                        "code": state_update.get("code", ""),
                        "test_results": state_update.get("test_results", ""),
                        "review_comments": state_update.get("review_comments", ""),
                        "status": state_update.get("status", "")
                    }
                    yield f"data: {json.dumps(packet)}\n\n"
        except Exception as e:
            error_packet = {"node": "ERROR", "error_message": str(e)}
            yield f"data: {json.dumps(error_packet)}\n\n"

    return Response(generate_stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    print(" Flask Server running on http://localhost:5000")
    server.run(host="0.0.0.0", port=5006, debug=True)