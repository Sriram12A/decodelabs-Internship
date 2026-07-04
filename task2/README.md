# AI Marketing & Image Generator

A Flask application using asynchronous Groq API calls to generate high-converting marketing copy and dynamically generate relevant visual URLs using the Pollinations AI proxy.

## Features
- Generates marketing copy asynchronously using Groq API (llama-3.3-70b-versatile).
- Automatically generates image prompts based on product descriptions and proxies them through `image.pollinations.ai`.
- Clean web interface to input product info, platform target, and desired tone.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
