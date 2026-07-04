import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder=".")

# Configure Groq API
API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """You are a strict, analytical Code Compiler and Interpreter. Your sole purpose is to parse the given code, find any syntax, runtime, or logical errors, and report them exactly like compiler error traces. Do not write friendly greetings. 

Your response MUST exactly include these two markdown headers:
## BUG_REPORT
## REFACTORED_CODE

Under ## BUG_REPORT, act like a compiler outputting errors. Use direct, concise bullet points to explain exactly what is broken (e.g., syntax errors, missing imports, logic faults).
Under ## REFACTORED_CODE, provide a single, valid Markdown-fenced code block with the corrected code that will successfully compile and run.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/review", methods=["POST"])
def review_code():
    if not API_KEY:
        return jsonify({"error": "Groq API key is missing. Please configure GROQ_API_KEY in the environment."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    # 1. Input & Payload Capture (File Ingestion)
    try:
        raw_code = file.read().decode('utf-8')
    except UnicodeDecodeError:
        return jsonify({"error": "Validation Flag: The uploaded file contains binary or unexpected characters and cannot be decoded safely."}), 400
    except PermissionError:
        return jsonify({"error": "Safely rejected: Insufficient permissions to read the uploaded file stream."}), 403
    except FileNotFoundError:
        return jsonify({"error": "Clean exit: File not found during payload capture."}), 404
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred during file ingestion: {str(e)}"}), 500

    # 2. Context Orchestration & The LLM Taming Matrix (using Groq)
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Please review the following code payload:\n\n```\n{raw_code}\n```"}
            ]
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        ai_text = response.json()["choices"][0]["message"]["content"]
        
        # 3. Structured Output Validation
        if "## BUG_REPORT" not in ai_text or "## REFACTORED_CODE" not in ai_text:
            return jsonify({
                "error": "Pipeline Validation Failure: The model failed to return both explicit section headers (## BUG_REPORT and ## REFACTORED_CODE). Malformed report rejected."
            }), 422
            
        return jsonify({
            "success": True,
            "report": ai_text
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Groq API Connection Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"AI Context Orchestration Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
