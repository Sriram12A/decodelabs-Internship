# Intelligent Code Compiler & Interpreter

An automated, AI-powered Code Architecture & Analysis tool that acts as a strict, tireless compiler and interpreter. The application securely ingests raw source code files and utilizes Groq's high-speed inference engine to aggressively parse code, instantly identifying syntax, runtime, and logical errors exactly like a traceback compiler log.

## 🚀 Features & Production-Grade Architecture

### 1. Ingestion Phase
- **IDE-Quality Terminal UI**: Built with HTML5 and Tailwind CSS. The output is dynamically rendered utilizing `marked.js` and `highlight.js` (Tokyo Night Dark theme).
- **Context Manager Triage**: The Flask backend explicitly streams uploads into memory via byte decoding, utilizing `try/catch` triage blocks to instantly block binary uploads (`UnicodeDecodeError`), reject unauthorized files (`PermissionError`), and gracefully handle missing streams.
- **Format Locking**: Only accepts `.py`, `.js`, and `.java` files out of the box.

### 2. Context Orchestration & LLM Taming
- **Groq LPU Engine**: Integrates the Groq API (`llama-3.1-8b-instant`) for incredibly fast token generation, mimicking the speed of an actual compiler.
- **Persona Locking**: The `SYSTEM_PROMPT` enforces strict constraints locking the model into a cold, analytical Compiler. It strictly disables conversational pleasantries and exclusively outputs trace-level bug reports.

### 3. Structured Validation
- **Architectural Gatekeeping**: The backend performs post-generation string validation enforcing the presence of exact Markdown headers (`## BUG_REPORT` and `## REFACTORED_CODE`). Any malformed response from the model is rejected with a `422 Unprocessable Entity` before it ever reaches the frontend client.

## 🛠️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd task4
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
   Create a `.env` file in the root directory and add your Groq API credentials. This file is safely excluded from version control via `.gitignore`.
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

5. **Run the Server:**
   ```bash
   python app.py
   ```
   The compiler application will boot up at `http://127.0.0.1:5000`. 
