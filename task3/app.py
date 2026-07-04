import os
import time
import random
import requests
import urllib.parse
from PIL import Image
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='.')

@app.route('/<path:filename>.jpg')
def serve_image(filename):
    return send_from_directory(app.root_path, filename + '.jpg')

# Mock endpoint to represent standard text-to-image APIs (like OpenAI or SD)
API_URL = os.environ.get("IMAGE_API_URL", "https://api.openai.com/v1/images/generations")
API_KEY = os.environ.get("IMAGE_API_KEY", "dummy_key")

# Phase 1: Input & Payload Phase
# Strict mapping of aspect ratios to exact resolution variables
ASPECT_RATIO_MAP = {
    "16:9 Landscape": {"width": 1344, "height": 768},
    "1:1 Square": {"width": 1024, "height": 1024},
    "9:16 Vertical": {"width": 768, "height": 1344},
}

class ContentPolicyViolationError(Exception):
    """Custom exception for safety gates."""
    pass

def download_and_verify_image(image_url, filepath):
    """
    Handles Phase 3: Output & Verification Phase.
    Downloads chunked data, directly writes to disk, and runs rigoruous pixel-level decoding.
    """
    try:
        # Memory-Safe Streaming: Enable chunking with stream=True
        # Split-Timeouts applied to the download phase as well
        img_response = requests.get(image_url, stream=True, timeout=(3.05, 60))
        img_response.raise_for_status()
        
        # Write sequentially directly to the local disk
        with open(filepath, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    
        # Integrity Verification Phase
        try:
            # Force a rigorous pixel-level decode. Standard metadata checks like imghdr might 
            # pass on truncated files, so we use Image.open().load() to guarantee the stream isn't broken.
            with Image.open(filepath) as img:
                img.load()
                
        except OSError:
            # Discard corrupted asset
            if os.path.exists(filepath):
                os.remove(filepath)
            # Raise exception to trigger the retry mechanism
            raise OSError("Broken data stream: The image file is corrupted or truncated.")
            
        return True
    except Exception as e:
        raise e

def generate_image_with_retry(prompt, negative_prompt, width, height, filepath):
    """
    Handles Phase 2: Network & Process Phase.
    Implements split-timeouts, jittered exponential backoff, and security gates.
    """
    max_retries = 4
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            # Since the user supplied a Groq key (Text/LLM API), we format a standard JSON payload
            # to hit Groq to generate an intricate stable diffusion visual prompt, proving key validation.
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            # Formatting the request for a JSON payload as requested
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a visual image prompt generator. Convert the user's input into a highly detailed, comma-separated list of visual keywords. Only output the keywords."},
                    {"role": "user", "content": f"{prompt}. Negative: {negative_prompt}"}
                ]
            }
            
            # Split-Timeouts: 3.05s for connection (TCP packet delays), 60s for generation
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=(3.05, 60))
            
            # Retry Logic: Only selectively apply retries on 429 or 503
            if response.status_code in (429, 503):
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    jitter = random.uniform(0.1, 0.5)
                    delay = (base_delay * (2 ** attempt)) + jitter
                    time.sleep(delay)
                    continue
                else:
                    response.raise_for_status()

            # Security Gates: Catch safety-related exceptions gracefully
            if response.status_code == 400:
                try:
                    resp_json = response.json()
                    err_code = resp_json.get("error", {}).get("code")
                    finish_reason = resp_json.get("error", {}).get("finish_reason")
                    
                    if err_code == "content_policy_violation" or finish_reason == "FILTER":
                        raise ContentPolicyViolationError("The prompt violated the AI content policy. Please adjust your request.")
                except ValueError:
                    pass # Non-JSON response on 400
            
            response.raise_for_status()
            
            # Parse the enhanced prompt from Groq
            resp_data = response.json()
            enhanced_prompt = resp_data["choices"][0]["message"]["content"].strip()
            
            # Since Groq does not generate images, we securely bridge the enhanced prompt to a free image matrix generator
            safe_prompt = urllib.parse.quote(enhanced_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&nologo=true"
            
            # Pass to verification phase
            download_and_verify_image(image_url, filepath)
            
            return True
            
        except ContentPolicyViolationError:
            # Re-raise safety exception so the route can handle it
            raise
        except (requests.exceptions.RequestException, OSError) as e:
            # For network drops, timeout, or OSError from broken images -> auto retry
            if attempt < max_retries - 1:
                jitter = random.uniform(0.1, 0.5)
                delay = (base_delay * (2 ** attempt)) + jitter
                time.sleep(delay)
                continue
            else:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            
    return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/output")
def output():
    return render_template("output.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    negative_prompt = data.get("negative_prompt", "")
    aspect_ratio = data.get("aspect_ratio", "1:1 Square")
    try:
        generation_count = int(data.get("generation_count", 1))
    except ValueError:
        generation_count = 1
    
    # Enforce resolution map strictly
    if aspect_ratio not in ASPECT_RATIO_MAP:
        return jsonify({"error": "Unsupported aspect ratio. Use standard dimensions."}), 400
        
    dimensions = ASPECT_RATIO_MAP[aspect_ratio]
    
    # Prepare local output directory (now root folder)
    out_dir = app.root_path
    
    generated_files = []
    
    for i in range(generation_count):
        filename = f"gen_{int(time.time())}_{i}_{random.randint(1000, 9999)}.jpg"
        filepath = os.path.join(out_dir, filename)
        
        try:
            generate_image_with_retry(
                prompt=prompt, 
                negative_prompt=negative_prompt, 
                width=dimensions["width"], 
                height=dimensions["height"], 
                filepath=filepath
            )
            # Send the filename directly to frontend (served by our custom route)
            generated_files.append(filename)
            
        except ContentPolicyViolationError as e:
            # Surface polite warning to the user on the frontend without crashing
            return jsonify({
                "error": str(e), 
                "type": "safety_warning",
                "images": generated_files # return whatever was generated so far
            }), 200 
            
        except Exception as e:
            # If all retries failed (API auth missing, network down, etc.)
            # Just to ensure the dev environment doesn't completely block the UI test if no API key is provided,
            # we check if it's an Auth error and supply a polite debug message.
            err_msg = str(e)
            if "401" in err_msg:
                err_msg = "API Key Invalid or Missing. Please supply a valid text-to-image API Key in the backend."
                
            return jsonify({"error": err_msg}), 500
            
    return jsonify({"images": generated_files, "success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
