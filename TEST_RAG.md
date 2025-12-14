# Testing RAG Integration

## ✅ What We Just Built

Your chatbot now has **RAG (Retrieval-Augmented Generation)**!

### How It Works:

```
User: "What is HbE disease?"
    ↓
1. Search Vector DB → Find relevant pages (45, 22, 21)
    ↓
2. Build Context → Page content + relevance scores
    ↓
3. Send to LLM → "Here's info from pages 45, 22, 21..."
    ↓
4. LLM Response → Smart answer based on YOUR database!
    ↓
5. Return with Citations → "According to Page 45..."
```

---

## Test It Now!

### Terminal 1: Start Backend with RAG

```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
source venv/bin/activate
python src/api.py
```

**You should see:**
```
🔍 Initializing RAG search engine...
📥 Loading embedding model for RAG...
💾 Connecting to ChromaDB...
✅ Connected to collection: hb_patterns (86 vectors)
✅ RAG search engine ready!
🚀 Starting Hemoglobin Pattern Chatbot API...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend

```bash
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck/ui
npm run dev
```

### Terminal 3: Test with curl (Optional)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is HbE disease?"}
    ]
  }'
```

---

## Expected Results

### Before RAG:
```
User: "What is HbE disease?"
AI: [Generic medical knowledge from training data]
Sources: None
```

### After RAG:
```
User: "What is HbE disease?"
AI: "Based on the database, Page 45 shows HbE zone at 24.9/25.1..."
Sources: 
  - Page 45 (Abnormal Hb Pattern.pdf) - Relevance: 56%
  - Page 22 (Abnormal Hb Pattern.pdf) - Relevance: 54%
  - Page 21 (Abnormal Hb Pattern.pdf) - Relevance: 53%
```

---

## Test Queries

Try these in your chatbot:

1. **"What is HbE disease?"**
   - Should cite pages 45, 22, 21

2. **"Show me beta thalassemia patterns"**
   - Should cite pages 25, 28, 11

3. **"What about elevated HbA2?"**
   - Should cite pages 45, 21, 39

4. **"Tell me about Constant Spring variant"**
   - Should cite page 32

5. **"Random unrelated question"**
   - Should say "No specific cases found" and use general knowledge

---

## What Changed

### Vector Database (NEW! ✅)
- Location: `vector_db/chroma_storage/`
- Vectors: 86 chunks from 46 pages
- Model: sentence-transformers/all-MiniLM-L6-v2
- Dimension: 384

### API Enhanced (UPDATED! ✅)
- `/api/chat` now searches database first
- Adds relevant context to LLM
- Returns real source citations
- Smarter, more specific answers

### Response Quality
- Before: Generic medical knowledge
- After: Specific to YOUR patient database
- Citations: Real page numbers
- Relevance: Scored 0-100%

---

## Performance

### Query Time Breakdown:
```
User sends message
    ↓ (100ms) Vector search
    ↓ (10ms) Build context
    ↓ (2-3s) LLM generation
    ↓
Response with citations!

Total: ~3.2 seconds ✅
```

---

## Troubleshooting

### Backend won't start
```bash
# Make sure vector DB exists
ls -la vector_db/chroma_storage/

# If not, rebuild:
python src/build_vectordb.py
```

### No sources in response
- Check backend logs for "Searching database"
- Verify RAG engine initialized successfully
- Try more specific medical queries

### Low relevance scores
- Normal! 40-60% is good for medical text
- Adjust threshold in api.py (currently 0.3 = 30%)

---

## Next Steps (Phase 2)

Once basic RAG is working:
1. ✅ Add reference images (146 PDFs)
2. ✅ Visual pattern matching
3. ✅ Side-by-side comparisons
4. ✅ Reference gallery in UI

---

**Ready to test? Start the servers and try it out!** 🚀

