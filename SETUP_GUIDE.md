# HB Pattern Chatbot - Setup Guide

Complete step-by-step guide to set up and run your hemoglobin pattern chatbot.

## Prerequisites

- Python 3.8 or higher
- 5GB free disk space (10GB for Phase 2)
- Internet connection (for initial setup)
- macOS, Linux, or Windows

## Phase 1: Hybrid Setup (Recommended)

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd /Users/jc/Desktop/hbpatterncheck/hbpatterncheck

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected time:** 5-10 minutes

### Step 2: Install Ollama (Local LLM)

Ollama provides the local LLM for generating chat responses.

```bash
# Make the script executable
chmod +x setup_ollama.sh

# Run the setup script
./setup_ollama.sh
```

Or manually:
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the Llama3 model (4.7GB)
ollama pull llama3

# Verify installation
ollama list
```

**Expected time:** 10-15 minutes (depends on internet speed)

### Step 3: Configure API Keys

Edit the `.env` file (you may need to create it as it's gitignored):

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_api_key_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./vector_db/chroma_storage
EOF

# Edit with your actual OpenAI API key
nano .env
```

Replace `your_api_key_here` with your actual OpenAI API key.

**Get API key:** https://platform.openai.com/api-keys

**Cost:** One-time ~$5-10 for image descriptions

### Step 4: Extract PDF Content

```bash
python src/1_extract_pdf.py
```

This will:
- Extract all text from the PDF
- Extract all chromatograph images
- Save to `data/` directory

**Expected output:**
- `data/pdf_text.json` - Text content
- `data/extracted_images/` - Chromatograph images
- `data/image_metadata.json` - Image metadata

**Expected time:** 1-2 minutes

### Step 5: Generate Image Descriptions

```bash
python src/2_describe_images.py
```

This sends each chromatograph to GPT-4V for detailed medical analysis.

**Expected output:**
- `data/image_descriptions.json` - Descriptions of all images

**Expected time:** 5-10 minutes (depends on number of images)

**Cost:** ~$0.01 per image

### Step 6: Build Vector Database

```bash
python src/3_build_vectordb.py
```

This creates the searchable vector database with embeddings.

**Expected output:**
- `vector_db/chroma_storage/` - Persistent ChromaDB

**Expected time:** 2-5 minutes

### Step 7: Test Query Engine (Optional)

```bash
python src/4_query_engine.py
```

This runs test queries to verify everything works.

**Expected time:** 1-2 minutes

### Step 8: Launch Chatbot

```bash
streamlit run src/5_app.py
```

The chatbot will open in your browser at http://localhost:8501

**🎉 You're done with Phase 1!**

---

## Phase 2: Fully Local Setup (Optional)

Transition to 100% local operation for complete privacy.

### Step 1: Install Additional Dependencies

```bash
pip install -r requirements-local.txt
```

**Expected time:** 5-10 minutes

### Step 2: Pull Local Vision Model

```bash
ollama pull llava:13b
```

**Expected time:** 15-20 minutes (7.3GB download)

### Step 3: Replace Image Descriptions (Optional)

If you want to regenerate descriptions using local LLaVA:

```bash
python src/2_describe_images.py --local
```

Or keep your existing GPT-4V descriptions (recommended).

### Step 4: Build CLIP Image Index (Optional)

For direct visual similarity search:

```bash
python src/clip_embeddings.py
```

This enables true image-to-image pattern matching.

**🎉 You're now fully local!**

---

## Verification Checklist

Run these tests to verify your setup:

```bash
# Test extraction
python tests/test_extraction.py

# Test embeddings
python tests/test_embeddings.py

# Test retrieval
python tests/test_retrieval.py
```

All tests should pass ✅

---

## Troubleshooting

### Ollama not running

**Error:** "Error: Ollama is not running"

**Fix:**
```bash
ollama serve
```

Run this in a separate terminal window.

### Import errors

**Error:** "ModuleNotFoundError: No module named 'X'"

**Fix:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### PDF not found

**Error:** "PDF not found at data/Abnormal Hb Pattern(pdf).pdf"

**Fix:**
Ensure the PDF file is in the `data/` directory with the exact name.

### OpenAI API errors

**Error:** "OpenAI API key not configured"

**Fix:**
- Check `.env` file exists
- Verify API key is correct
- Check account has credits: https://platform.openai.com/usage

### ChromaDB not found

**Error:** "Error connecting to vector database"

**Fix:**
```bash
# Rebuild the vector database
python src/3_build_vectordb.py
```

### Out of memory

**Error:** Various memory errors

**Fix:**
- Close other applications
- Use smaller batch sizes in config.yaml
- Reduce chunk_size in config.yaml

---

## Usage Examples

### Text Queries

1. "What are the characteristics of HbE disease?"
2. "Show cases with elevated HbA2"
3. "Find patterns similar to HbH disease"
4. "What retention times indicate beta thalassemia?"

### Image Queries

1. Upload a chromatograph image
2. Enter a query like "Find similar patterns"
3. System will describe the image and find similar cases

---

## Performance Tuning

### Speed up queries

Edit `config/config.yaml`:

```yaml
retrieval:
  top_k: 3  # Reduce from 5
  
llm:
  max_tokens: 300  # Reduce from 500
```

### Improve accuracy

```yaml
retrieval:
  top_k: 10  # Increase retrieval

chunking:
  chunk_size: 1500  # Larger chunks
  chunk_overlap: 300
```

---

## Maintenance

### Update the database

If you modify the PDF:

```bash
# 1. Re-extract
python src/1_extract_pdf.py

# 2. Re-describe images (if new images)
python src/2_describe_images.py

# 3. Rebuild vector database
python src/3_build_vectordb.py
```

### Clear and rebuild

```bash
# Delete vector database
rm -rf vector_db/chroma_storage/

# Rebuild from scratch
python src/3_build_vectordb.py
```

---

## Next Steps

- Customize prompts in `src/4_query_engine.py`
- Adjust UI in `src/5_app.py`
- Add more PDFs to the database
- Fine-tune retrieval parameters
- Deploy to cloud (Streamlit Cloud, AWS, etc.)

---

## Support

For issues or questions:
1. Check this setup guide
2. Review error messages carefully
3. Check that all prerequisites are installed
4. Verify all setup steps completed successfully

**Enjoy your HB Pattern Chatbot! 🔬🤖**

