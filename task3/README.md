# Multimodal Image Generation Studio

A production-grade visual application that translates natural language text descriptions into high-quality digital artwork. The studio securely interfaces with standard text-to-image API endpoints (including LLM-enhanced prompt pipelines) to generate and display digital art seamlessly.

## 🚀 Features & Production-Grade Architecture

### 1. Input & Payload Phase
- **Immersive UI**: Built with HTML5 and Tailwind CSS. The workflow is cleanly separated into a dedicated input page and an output gallery.
- **Strict Resolution Mapping**: Aspect ratio inputs (e.g. `16:9 Landscape`) are strictly mapped to exact pixel boundaries (`1344x768`) to prevent API dimension rejections before transmitting the payload.

### 2. Network & Process Phase
- **Advanced API Bridging**: Supports using text-centric API keys (like Groq) by generating enhanced diffusion prompts and bridging them to free open matrix endpoints (Pollinations.ai), all while enforcing a strict JSON payload architecture.
- **Split-Timeouts**: Network requests explicitly enforce `timeout=(3.05, 60)` to accommodate early TCP packet delays without hanging on slow GPU diffusion matrix generation.
- **Jittered Backoff & Retry Logic**: Automatically catches HTTP `429` and `503` errors, applying exponential backoff with randomized jitter to gracefully manage API rate limits.
- **Security Gates**: Actively catches model content policy violations gracefully and safely relays frontend warnings without crashing the server.

### 3. Output & Verification Phase
- **Memory-Safe Streaming**: Avoids loading raw high-res images directly into RAM. Enforces chunked stream downloading `iter_content(chunk_size=65536)` to save sequentially to disk.
- **Strict Integrity Verification**: Bypasses standard header/metadata checks that fail on dropped connections. It executes a rigorous pixel-level decode (`Image.open().load()`) inside an `OSError` catch block. Corrupt or truncated files are instantly deleted and scheduled for automatic redownload.

## 🛠️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd task3
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory (this is automatically ignored by git) and add your API credentials:
   ```env
   # Example: Using a Groq API Key to enhance prompts
   IMAGE_API_KEY=gsk_your_api_key_here
   ```

5. **Run the Server:**
   ```bash
   python app.py
   ```
   The application will be running at `http://127.0.0.1:5000`. 
