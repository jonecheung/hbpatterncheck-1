# Troubleshooting Guide

Common issues and solutions for the HB Pattern Chatbot.

---

## Critical Issue: `ModuleNotFoundError: No module named '_lzma'`

### Problem
When running `python3 src/3_build_vectordb.py`, you get:
```
ModuleNotFoundError: No module named '_lzma'
```

### Why This Happens
Python was compiled without xz/lzma support. This is common with pyenv installations on macOS.

### Solution 1: Reinstall Python with xz (Recommended)

```bash
# 1. Install xz library
brew install xz

# 2. Reinstall Python via pyenv
pyenv install 3.12.11

# 3. Set it as local version
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck
pyenv local 3.12.11

# 4. Verify lzma works
python3 -c "import lzma; print('lzma OK')"

# 5. Reinstall dependencies
pip3 install -r requirements.txt
```

### Solution 2: Use Python from python.org

```bash
# 1. Download Python 3.12 from python.org
# https://www.python.org/downloads/mac-osx/

# 2. Install it (includes lzma by default)

# 3. Use that Python
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m pip install -r requirements.txt

# 4. Update scripts to use that Python
```

### Solution 3: Use Python 3.11 Instead

```bash
# Python 3.11 sometimes has better compatibility
pyenv install 3.11.9
pyenv local 3.11.9
python3 -c "import lzma; print('lzma OK')"
pip3 install -r requirements.txt
```

### Solution 4: Use Conda/Miniconda

```bash
# Conda includes all necessary system libraries
brew install miniconda
conda create -n hbchatbot python=3.12
conda activate hbchatbot
pip install -r requirements.txt
```

---

## Issue: Ollama Not Found

### Symptoms
```
ollama: command not found
```

### Solution

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama3 model
ollama pull llama3

# Verify
ollama list
```

---

## Issue: ChromaDB Errors

### Symptoms
```
sqlite3.OperationalError: database is locked
```
or
```
Collection already exists
```

### Solution

```bash
# Delete and rebuild database
rm -rf vector_db/chroma_storage/
python3 src/3_build_vectordb.py
```

---

## Issue: OpenAI API Errors

### Symptoms
```
openai.error.AuthenticationError: Invalid API key
```

### Solution

1. Check `.env` file exists:
```bash
ls -la .env
```

2. Verify API key format:
```bash
cat .env | grep OPENAI_API_KEY
```

Should be: `OPENAI_API_KEY=sk-...`

3. Get new key: https://platform.openai.com/api-keys

4. Test key:
```bash
export OPENAI_API_KEY=sk-your-key
python3 -c "from openai import OpenAI; print(OpenAI().models.list())"
```

---

## Issue: Slow Embedding Generation

### Symptoms
Vector database build takes > 10 minutes

### Solutions

**Option 1: Use smaller embedding model**

Edit `config/config.yaml`:
```yaml
embeddings:
  model: "sentence-transformers/all-MiniLM-L6-v2"  # Fast, 384 dim
  # Instead of: "all-mpnet-base-v2"  # Slower, 768 dim
```

**Option 2: Reduce chunk size**

Edit `config/config.yaml`:
```yaml
chunking:
  chunk_size: 500    # Smaller = fewer chunks
  chunk_overlap: 100
```

**Option 3: Use CPU optimized version**

```bash
pip3 install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Issue: Streamlit Won't Start

### Symptoms
```
streamlit: command not found
```

### Solution

```bash
# Reinstall streamlit
pip3 install streamlit

# Or use python -m
python3 -m streamlit run src/5_app.py
```

---

## Issue: Slow Ollama Responses

### Symptoms
Each query takes > 10 seconds

### Solutions

**Check Ollama is running:**
```bash
ollama list
```

**Use smaller model:**
```bash
# Instead of llama3 (8B), use:
ollama pull llama3.2:1b  # Much faster, 1B params

# Update config.yaml:
llm:
  model: "llama3.2:1b"
```

**Increase context limit:**
```bash
# Edit config.yaml
llm:
  max_tokens: 300  # Reduce from 500
```

**Check CPU usage:**
```bash
# Ollama should show in Activity Monitor
# If not, restart:
ollama serve
```

---

## Issue: No Images Extracted from PDF

### Symptoms
```
Total images extracted: 0
```

### Why This Happens
The chromatograph images may be:
1. Vector graphics (not raster images)
2. Embedded as text/drawings
3. In a format PyMuPDF can't extract

### Solutions

**Option 1: Accept text-only mode**
- The chatbot will work fine with just text
- Most diagnostic info is in the text anyway

**Option 2: Convert PDF to image-based PDF**
```bash
# Use Adobe Acrobat or online tool to "flatten" PDF
# Then re-run extraction
```

**Option 3: Add Phase 2 - Manual image extraction**
- Extract images manually
- Place in `data/extracted_images/`
- Run GPT-4V description script

**Option 4: Skip images entirely**
- Focus on text-based search
- Still very useful for case finding

---

## Issue: "Collection already exists" Error

### Symptoms
```
ValueError: Collection hb_patterns already exists
```

### Solution

The script should auto-delete existing collections, but if not:

```python
# Add to config.yaml or use CLI:
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./vector_db/chroma_storage')
client.delete_collection(name='hb_patterns')
print('Collection deleted')
"
```

Then re-run:
```bash
python3 src/3_build_vectordb.py
```

---

## Issue: Out of Memory Errors

### Symptoms
```
RuntimeError: [enforce fail at alloc_cpu.cpp:73]
```

### Solutions

**Reduce batch size:**

Edit `src/3_build_vectordb.py`:
```python
batch_size = 50  # Instead of 100
```

**Use smaller model:**
```yaml
# config.yaml
embeddings:
  model: "sentence-transformers/all-MiniLM-L6-v2"  # 80MB
  # Not: "all-mpnet-base-v2"  # 420MB
```

**Close other apps:**
- Free up RAM before running
- Monitor Activity Monitor

---

## Issue: Import Errors

### Symptoms
```
ModuleNotFoundError: No module named 'langchain'
```

### Solution

```bash
# Reinstall all dependencies
pip3 install -r requirements.txt

# Verify installations
pip3 list | grep -E "(langchain|chromadb|streamlit)"
```

---

## Issue: PDF Not Found

### Symptoms
```
❌ Error: PDF not found at data/Abnormal Hb Pattern(pdf).pdf
```

### Solution

```bash
# Check PDF location
ls -la data/

# Move if needed
mv "Abnormal Hb Pattern(pdf).pdf" data/

# Or update config.yaml with correct path
```

---

## Issue: Retrieval Returns No Results

### Symptoms
Chatbot says "I don't have enough information"

### Solutions

**Lower similarity threshold:**

Edit `config/config.yaml`:
```yaml
retrieval:
  top_k: 5
  similarity_threshold: 0.5  # Lower = more results (was 0.7)
```

**Increase top_k:**
```yaml
retrieval:
  top_k: 10  # More results
```

**Check database has content:**
```bash
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./vector_db/chroma_storage')
collection = client.get_collection('hb_patterns')
print(f'Vectors: {collection.count()}')
"
```

Should show 62 vectors.

---

## Issue: Poor Quality Responses

### Symptoms
LLM gives generic or incorrect answers

### Solutions

**Improve prompt template:**

Edit `src/4_query_engine.py`, update the system prompt to be more specific.

**Use better LLM:**
```bash
# Use larger Llama model
ollama pull llama3:70b  # Much better, but slower
```

**Adjust temperature:**
```yaml
# config.yaml
llm:
  temperature: 0.3  # Lower = more factual (was 0.7)
```

**Retrieve more context:**
```yaml
retrieval:
  top_k: 8  # More context (was 5)
```

---

## Debug Mode

### Enable Verbose Logging

Add to scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check What's in Vector DB

```python
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./vector_db/chroma_storage')
collection = client.get_collection('hb_patterns')

# Get sample documents
results = collection.get(limit=3, include=['documents', 'metadatas'])
for doc, meta in zip(results['documents'], results['metadatas']):
    print(f'Page {meta[\"page\"]}: {doc[:100]}...')
"
```

### Test Embeddings

```python
python3 -c "
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embedding = model.encode('test query')
print(f'Embedding shape: {embedding.shape}')
print('Embeddings working!')
"
```

---

## Getting Help

If none of these solutions work:

1. **Check logs carefully** - Error messages usually indicate the issue
2. **Verify each component separately:**
   - Python lzma: `python3 -c "import lzma"`
   - Ollama: `ollama list`
   - Dependencies: `pip3 list`
   - PDF: `ls -la data/`
3. **Start fresh:**
   ```bash
   rm -rf vector_db/
   pip3 install -r requirements.txt --force-reinstall
   python3 src/3_build_vectordb.py
   ```

---

## Prevention Tips

- **Use virtual environments** to avoid dependency conflicts
- **Test components individually** before running full pipeline
- **Keep backups** of working configurations
- **Document any system-specific fixes** you discover


