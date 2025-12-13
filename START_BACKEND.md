# Start Backend API Guide

## Quick Start

### 1. Make Sure Virtual Environment is Activated

```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
source venv/bin/activate

# You should see (venv) in your prompt
```

### 2. Install New Dependencies (FastAPI, etc.)

```bash
pip install -r requirements.txt
```

### 3. Add Your OpenRouter API Key

Make sure `.env` file has your real API key:

```bash
# Open .env file
open .env

# Replace this line with your real key:
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### 4. Test OpenRouter Connection (Optional)

```bash
python src/openrouter_client.py
```

You should see:
```
✅ Chat test passed: HbE disease is...
✅ Connection test: Passed
```

### 5. Start the Backend Server

```bash
python src/api.py
```

You should see:
```
🚀 Starting Hemoglobin Pattern Chatbot API...
📍 API will be available at: http://localhost:8000
📚 Docs available at: http://localhost:8000/docs
🔗 Frontend should connect to: http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Test the API

### Option 1: Visit API Docs

Open in browser: http://localhost:8000/docs

You'll see interactive API documentation where you can test endpoints!

### Option 2: Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Chat test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is HbE disease?"}
    ]
  }'
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/api/chat` | POST | Send chat message, get AI response |
| `/api/upload-image` | POST | Upload chromatograph image |
| `/api/analyze-image` | POST | Analyze image with Vision API |
| `/api/references` | GET | Get reference categories |
| `/api/search` | POST | Search vector DB (coming soon) |

---

## What the API Does

### Chat Flow
```
React Frontend
    ↓ POST /api/chat
Backend API (FastAPI)
    ↓ Adds medical context
OpenRouter (Llama 3.1)
    ↓ AI response
Backend API
    ↓ Returns JSON
React Frontend displays
```

### Image Analysis Flow
```
User uploads image
    ↓ POST /api/upload-image
Backend receives base64
    ↓ POST /api/analyze-image
OpenRouter Vision (GPT-4V)
    ↓ Pattern analysis
Backend adds sources
    ↓ Returns JSON
Frontend displays results
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn src.api:app --port 8001
```

### OpenRouter API Key Error
```
ValueError: OPENROUTER_API_KEY not found
```

**Solution:** Make sure `.env` file exists and has your key

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### CORS Errors from Frontend
The API is configured to accept requests from:
- http://localhost:5173 (Vite)
- http://localhost:3000 (React)
- http://localhost:8501 (Streamlit)

If your frontend runs on different port, edit `src/api.py`:
```python
allow_origins=[
    "http://localhost:YOUR_PORT",  # Add your port
    ...
]
```

---

## Next Steps

Once backend is running:

1. ✅ Keep this terminal open (server running)
2. ✅ Open new terminal for frontend
3. ✅ Start frontend: `cd ui && npm run dev`
4. ✅ Frontend will connect to http://localhost:8000
5. ✅ Test chat functionality

---

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## Development Mode

The server runs with `reload=True`, so:
- Any changes to Python files auto-reload
- No need to restart after code changes
- Great for development!

---

**Ready to connect the frontend!** 🚀

Once backend is running, start the frontend and they'll communicate automatically!

