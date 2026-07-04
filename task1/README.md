# AI Chat Assistant

A Flask-based AI chat assistant utilizing the Groq API for fast completions.

## Features
- Interactive and responsive chat interface.
- Sliding window history to manage context window length dynamically.
- Error handling for API limits and network issues.
- Uses `waitress` for production-grade serving.

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
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   FLASK_ENV=development  # optional, for dev mode
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
