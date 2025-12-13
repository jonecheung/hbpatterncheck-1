# Environment Setup Guide

## Overview

Your project has two parts:
1. **Frontend (React)** - in `ui/` folder
2. **Backend (Python API)** - in `src/` folder (we'll create this)

Each needs its own environment variables.

---

## Part 1: Frontend Environment Variables

### Create file: `ui/.env`

```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck/ui
touch .env
```

Then open `ui/.env` and add:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Hemoglobin Pattern Chatbot
```

**What these do:**
- `VITE_API_URL` - Points to your backend API (we'll create this)
- `VITE_APP_NAME` - App name for display

---

## Part 2: Backend Environment Variables

### Create file: `.env` (in project root)

```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
touch .env
```

Then open `.env` and add:

```env
# OpenRouter API Key (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# OpenRouter Settings
OPENROUTER_APP_NAME=HB-Pattern-Chatbot
OPENROUTER_SITE_URL=http://localhost:8000

# Optional: Local embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./vector_db/chroma_storage
```

**Important:** Replace `sk-or-v1-your-actual-key-here` with your real OpenRouter API key!

---

## How to Get OpenRouter API Key

1. Go to: https://openrouter.ai/
2. Sign up or log in
3. Go to **Keys** section
4. Click **Create Key**
5. Copy the key (starts with `sk-or-v1-...`)
6. Paste it into your `.env` file

---

## File Structure After Setup

```
hbpatterncheck/
├── .env                    ← Backend API key here (Python)
├── ui/
│   └── .env               ← Frontend config here (React)
└── ...
```

---

## Security Notes

✅ `.env` files are in `.gitignore` - never committed to git
✅ API keys stay on backend - never exposed to browser
✅ Frontend only knows backend URL, not API key

---

## Quick Setup Commands

Run these in your terminal:

```bash
# Navigate to project
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck

# Create backend .env
cat > .env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_APP_NAME=HB-Pattern-Chatbot
OPENROUTER_SITE_URL=http://localhost:8000
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./vector_db/chroma_storage
EOF

# Create frontend .env
cat > ui/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Hemoglobin Pattern Chatbot
EOF

echo "✅ Environment files created!"
echo "⚠️  Don't forget to add your real OpenRouter API key to .env"
```

---

## Next Steps

After creating these files:

1. ✅ Add your OpenRouter API key to root `.env`
2. ✅ Build the backend API (Python FastAPI)
3. ✅ Connect frontend to backend
4. ✅ Test the integration

Ready to build the backend API? 🚀

