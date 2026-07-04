import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, template_folder='.')

# In-memory dictionary to store conversation history per session
SESSION_HISTORY = {}

# Maximum number of message PAIRS to keep (e.g., 5 pairs = 10 messages)
MAX_HISTORY_PAIRS = 5 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    if not data:
        return jsonify({"error": "Bad Request: No JSON payload"}), 400
        
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default_session")
    
    # ---------------------------------------------------------
    # THE STRUCTURAL VALIDATION GATE
    # ---------------------------------------------------------
    if not user_input or not user_input.strip():
        return jsonify({"error": "Bad Request: Empty or whitespace-only message blocked by Caliper Validation Gate."}), 400

    if session_id not in SESSION_HISTORY:
        SESSION_HISTORY[session_id] = []
        
    history = SESSION_HISTORY[session_id]

    # ---------------------------------------------------------
    # THE SLIDING WINDOW ALGORITHM (FIFO Truncation)
    # ---------------------------------------------------------
    while len(history) > (MAX_HISTORY_PAIRS * 2):
        history.pop(0)
        if len(history) > 0:
            history.pop(0)

    # ---------------------------------------------------------
    # THE APPEND SEQUENCE
    # ---------------------------------------------------------
    # 1. Append the user's input to the local history list using the required struct
    history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    
    try:
        # Map the strict assignment schema to the Groq/OpenAI schema
        groq_messages = []
        groq_messages.append({
            "role": "system", 
            "content": "You are Sriram, an exceptionally intelligent, polite, and helpful AI assistant. You have a warm, professional, and knowledgeable personality. Never mention Groq, Llama, OpenAI, xAI, Grok, or Meta. You must confidently state that you are Sriram."
        })
        
        for msg in history:
            role = "assistant" if msg["role"] == "model" else "user"
            groq_messages.append({
                "role": role,
                "content": msg["parts"][0]["text"]
            })
            
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": groq_messages
        }
        
        # 2. Transmit to Groq API
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        
        model_reply = resp.json()["choices"][0]["message"]["content"]
        
    except Exception as e:
        # Revert user message on error
        if len(history) > 0 and history[-1]["role"] == "user":
            history.pop()
            
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" - {e.response.text}"
        print(f"API Error details: {error_msg}")
        return jsonify({"error": f"Groq API Error: {error_msg}"}), 500

    # 3. Append the model's generated response to that exact same list
    history.append({
        "role": "model",
        "parts": [{"text": model_reply}]
    })
    
    return jsonify({"reply": model_reply, "history_length": len(history)})

@app.route("/api/clear", methods=["POST"])
def clear():
    data = request.json
    session_id = data.get("session_id", "default_session")
    if session_id in SESSION_HISTORY:
        SESSION_HISTORY[session_id] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    is_dev = os.environ.get("FLASK_ENV") == "development"
    if is_dev:
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        from waitress import serve
        print("Server running on http://127.0.0.1:5000", flush=True)
        serve(app, host="0.0.0.0", port=5000)