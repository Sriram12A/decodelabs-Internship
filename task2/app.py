import os
import asyncio
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import AsyncGroq
import urllib.parse

load_dotenv(override=True)

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')

# The Groq client will be instantiated per-request to avoid asyncio event loop deadlocks

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/image")
def proxy_image():
    prompt = request.args.get("prompt", "")
    if not prompt:
        return "Missing prompt", 400
    
    encoded = urllib.parse.quote(prompt)
    seed = request.args.get("seed", "123")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={seed}"
    
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=30)
        from flask import Response
        return Response(res.read(), mimetype='image/jpeg')
    except Exception as e:
        print(f"Image proxy error: {e}")
        return str(e), 500

@app.route("/output")
def output_page():
    return render_template("output.html")

async def generate_marketing_copy(client, product_info, target_tool, tone):
    prompt = f"""You are an expert copywriter. Write highly persuasive, high-converting marketing copy for a product or service.
    
Product/Service Info: {product_info}
Platform/Tool: {target_tool}
Tone of Voice: {tone}

Please output only the marketing copy without any conversational filler. Format it beautifully with line breaks, emojis, and a clear structure (e.g., Headline, Hook, Body, Call to Action) tailored for {target_tool}."""

    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class marketing copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating copy: {e}")
        return f"Error generating copy: {str(e)}"

async def generate_visual_url(client, product_info, tone):
    prompt = f"""Write a short, highly descriptive image generation prompt (max 50 words) to create a highly accurate, 3D cinematic, hyper-realistic product image for the following product. 
    Product: {product_info}
    Style: {tone}, cinematic lighting, photorealistic, 8k resolution.
    Only return the prompt text without any other words."""
    
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
            stream=False,
        )
        image_prompt = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        # Fallback prompt
        image_prompt = f"Cinematic, hyper-realistic product shot of {product_info[:50]}, professional lighting, 8k"

    import re
    import random
    
    # Sanitize the prompt to remove any problematic characters or newlines
    image_prompt = image_prompt.replace('\n', ' ').replace('\r', ' ')
    image_prompt = re.sub(r'[^\w\s\.,-]', '', image_prompt)

    encoded_prompt = urllib.parse.quote(image_prompt)
    random_seed = random.randint(1, 100000)
    # Point the image URL to our local proxy instead of directly to pollinations
    image_url = f"/api/image?prompt={encoded_prompt}&seed={random_seed}"
    
    return image_url

@app.route("/api/generate", methods=["POST"])
async def generate():
    data = request.json
    product_info = data.get("product_info")
    target_tool = data.get("target_tool", "LinkedIn")
    tone = data.get("tone", "Professional")
    
    if not product_info:
        return jsonify({"error": "Product info is required"}), 400

    # Instantiate the client here within the active event loop
    client = AsyncGroq(
        api_key=os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
    )

    # Run both tasks concurrently using asyncio.gather
    copy_task = generate_marketing_copy(client, product_info, target_tool, tone)
    visual_task = generate_visual_url(client, product_info, tone)
    
    copy_result, image_url = await asyncio.gather(copy_task, visual_task)
    
    return jsonify({
        "copy": copy_result,
        "image_url": image_url
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    # Restart trigger for .env changes
