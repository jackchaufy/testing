# LangChain Agent Demo

This project includes a FastAPI backend and a simple frontend to demo a LangChain
agent that can call multiple tools and be controlled from a web UI.

## Backend

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your-key
   ```
3. Start the API server:
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## Frontend

The frontend is served by the backend at `http://localhost:8000`. If you prefer to
run it separately, you can use a simple static server:

```bash
cd frontend
python -m http.server 8000
```

Then open `http://localhost:8000/index.html` in your browser.
