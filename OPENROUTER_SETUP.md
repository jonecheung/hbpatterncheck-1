# OpenRouter Setup Guide

Using OpenRouter instead of OpenAI for the HB Pattern Chatbot.

---

## Why OpenRouter?

✅ **Cost-effective:** Often cheaper than direct OpenAI API  
✅ **Multiple models:** Access to GPT-4, Claude, Llama, Mistral, and more  
✅ **Unified API:** One API key for all models  
✅ **Flexible:** Switch models without code changes  

---

## Setup Steps

### 1. Get OpenRouter API Key

1. Go to: https://openrouter.ai/
2. Sign up / Log in
3. Go to **Keys** section
4. Create a new API key
5. Copy the key (starts with `sk-or-...`)

### 2. Create `.env` File

Create a file named `.env` in the project root:

```bash
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# Optional: OpenRouter settings
OPENROUTER_APP_NAME=HB-Pattern-Chatbot
OPENROUTER_SITE_URL=http://localhost:8501

# Embedding model (still local)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ChromaDB path
CHROMA_DB_PATH=./vector_db/chroma_storage
```

### 3. Update Configuration

Edit `config/config.yaml`:

```yaml
# Change this section:
llm:
  provider: "openrouter"  # Add this line
  model: "meta-llama/llama-3.1-8b-instruct"  # Or any OpenRouter model
  temperature: 0.7
  max_tokens: 500
  api_base: "https://openrouter.ai/api/v1"  # Add this line

# For image descriptions (if you have images):
vision:
  provider: "openrouter"  # Add this line
  model: "openai/gpt-4-vision-preview"  # Or other vision models
  api_base: "https://openrouter.ai/api/v1"  # Add this line
```

---

## Supported Models

### For Chat/LLM (query responses)

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| **meta-llama/llama-3.1-8b-instruct** | $ | Fast | Good |
| **anthropic/claude-3.5-sonnet** | $$$ | Medium | Excellent |
| **openai/gpt-4-turbo** | $$$ | Medium | Excellent |
| **openai/gpt-3.5-turbo** | $ | Fast | Good |
| **google/gemini-pro-1.5** | $$ | Fast | Very Good |
| **mistralai/mixtral-8x7b-instruct** | $ | Fast | Good |

**Recommended:** `meta-llama/llama-3.1-8b-instruct` (best value)

### For Image Descriptions (if needed)

| Model | Cost | Quality |
|-------|------|---------|
| **openai/gpt-4-vision-preview** | $$ | Excellent |
| **anthropic/claude-3.5-sonnet** | $$$ | Excellent |
| **google/gemini-pro-vision** | $ | Very Good |

---

## Code Changes Required

### Update `src/4_query_engine.py`

Replace Ollama client with OpenRouter:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_with_openrouter(prompt, model="meta-llama/llama-3.1-8b-instruct"):
    """Query using OpenRouter API"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "HB-Pattern-Chatbot"),
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a medical AI assistant specializing in hemoglobin pattern diseases."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
    
    result = response.json()
    return result['choices'][0]['message']['content']
```

### Update `src/2_describe_images.py`

For image descriptions with OpenRouter:

```python
def describe_image_with_openrouter(image_path: str) -> str:
    """Use OpenRouter (GPT-4V or Claude) to describe image"""
    
    import base64
    
    # Encode image
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "HB-Pattern-Chatbot"),
        },
        json={
            "model": "openai/gpt-4-vision-preview",  # Or claude-3.5-sonnet
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this hemoglobin chromatograph in detail..."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
    )
    
    return response.json()['choices'][0]['message']['content']
```

---

## Installation

No need to install Ollama! Just install Python dependencies:

```bash
pip install -r requirements.txt
```

Add `requests` if not already in requirements:
```bash
pip install requests
```

---

## Cost Comparison

### OpenRouter Pricing (Approximate)

**For your use case (62 text chunks, ~100 queries/month):**

| Model | Setup Cost | Per Query | Monthly |
|-------|-----------|-----------|---------|
| **Llama 3.1 8B** | $0 | $0.0001 | $0.01 |
| **GPT-3.5 Turbo** | $0 | $0.001 | $0.10 |
| **GPT-4 Turbo** | $0 | $0.01 | $1.00 |
| **Claude 3.5 Sonnet** | $0 | $0.015 | $1.50 |

**Recommended:** Llama 3.1 8B - **~$0.01/month** 🎉

### vs Local Ollama

| Aspect | OpenRouter | Local Ollama |
|--------|-----------|--------------|
| **Cost** | ~$0.01-1/mo | $0 |
| **Setup** | Easy | Medium |
| **Speed** | Fast (API) | Slower (local) |
| **Privacy** | Cloud | 100% Local |
| **Hardware** | None | CPU/RAM |

**If privacy is critical → Use Ollama**  
**If convenience is important → Use OpenRouter**

---

## Testing OpenRouter Connection

Test your API key:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    },
    json={
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "user", "content": "Say 'Hello, OpenRouter is working!'"}
        ]
    }
)

print(response.json())
```

Expected output:
```json
{
  "choices": [
    {
      "message": {
        "content": "Hello, OpenRouter is working!"
      }
    }
  ]
}
```

---

## Updated Architecture

### With OpenRouter (No Ollama Needed)

```
User Query
    ↓
Streamlit UI
    ↓
Query Engine (RAG)
    ↓
ChromaDB (Vector Search) → Top 5 Cases
    ↓
Context Builder
    ↓
OpenRouter API (Llama/GPT/Claude)
    ↓
Natural Language Response
```

### What's Local vs Cloud

**Local (Your Machine):**
- ✅ PDF extraction
- ✅ Text chunking
- ✅ Embeddings (sentence-transformers)
- ✅ Vector database (ChromaDB)
- ✅ Streamlit UI

**Cloud (OpenRouter):**
- ☁️ LLM chat responses
- ☁️ Image descriptions (optional)

---

## Quick Start with OpenRouter

### 1. Get API Key
https://openrouter.ai/ → Keys → Create

### 2. Create `.env`
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Update Scripts
Add OpenRouter functions to `src/4_query_engine.py`

### 4. Fix lzma Issue
See `TROUBLESHOOTING.md`

### 5. Build Vector DB
```bash
python3 src/3_build_vectordb.py
```

### 6. Launch Chatbot
```bash
streamlit run src/5_app.py
```

---

## Advantages of OpenRouter for Your Project

1. **No local GPU needed** - API handles computation
2. **Multiple models** - Try different models without reinstalling
3. **Cheaper than OpenAI** - Often 50% less expensive
4. **Fast setup** - Just API key, no model downloads
5. **Good for prototyping** - Iterate quickly

---

## Model Recommendations

### For Medical/Technical Content

**Best Quality:**
```yaml
llm:
  model: "anthropic/claude-3.5-sonnet"  # Best medical reasoning
```

**Best Value:**
```yaml
llm:
  model: "meta-llama/llama-3.1-8b-instruct"  # 100x cheaper
```

**Balanced:**
```yaml
llm:
  model: "openai/gpt-3.5-turbo"  # Good quality, reasonable cost
```

---

## Monitoring Costs

Check your usage:
1. Go to https://openrouter.ai/
2. Click on **Activity** or **Usage**
3. See per-query costs and monthly totals

Set spending limits:
1. Go to **Settings**
2. Set monthly budget limit
3. Get alerts when approaching limit

---

## Troubleshooting

### Error: "Invalid API key"
```bash
# Check .env file
cat .env | grep OPENROUTER_API_KEY

# Verify format: sk-or-v1-...
# Regenerate key if needed at openrouter.ai
```

### Error: "Model not found"
```bash
# Check available models at:
# https://openrouter.ai/models

# Update config.yaml with correct model name
```

### Slow responses
```bash
# Try faster model:
llm:
  model: "meta-llama/llama-3.1-8b-instruct"  # Fast
  # Instead of: "anthropic/claude-3-opus"  # Slow but best
```

---

## Summary

**OpenRouter Setup is Simpler:**
- ❌ No Ollama installation needed
- ❌ No large model downloads (4-7GB)
- ❌ No local GPU/CPU requirements
- ✅ Just API key + code changes
- ✅ Ready in 5 minutes

**Total cost for your use case: ~$0.01-1.00/month** depending on model choice.


