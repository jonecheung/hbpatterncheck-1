# Hemoglobin Pattern Disease Chatbot

AI-powered chatbot for searching and analyzing hemoglobin pattern disease cases using vector database and RAG (Retrieval-Augmented Generation).

## Features

- 🔍 **Text-based search**: Query patient cases using natural language
- 🖼️ **Image-based search**: Upload chromatograph images to find similar patterns
- 🤖 **AI-powered responses**: Uses LLM to provide contextual answers
- 🔒 **Privacy-focused**: Local vector database and LLM options
- 📊 **Visual pattern matching**: Compare chromatograph images

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama (for local LLM)

```bash
# Run the setup script
chmod +x setup_ollama.sh
./setup_ollama.sh
```

Or manually:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

### 3. Configure API Keys

Edit `.env` file and add your OpenAI API key (for Phase 1):
```
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Extract PDF Content

```bash
python src/1_extract_pdf.py
```

### 5. Generate Image Descriptions (Phase 1)

```bash
python src/2_describe_images.py
```

### 6. Build Vector Database

```bash
python src/3_build_vectordb.py
```

### 7. Run the Chatbot

```bash
streamlit run src/5_app.py
```

## Project Structure

```
hbpatterncheck/
├── data/                          # Data files
│   ├── Abnormal Hb Pattern(pdf).pdf
│   ├── extracted_images/          # Extracted chromatographs
│   ├── pdf_text.json             # Extracted text
│   └── image_descriptions.json    # Image descriptions
├── vector_db/                     # Vector database storage
│   └── chroma_storage/
├── src/                          # Source code
│   ├── 1_extract_pdf.py          # PDF extraction
│   ├── 2_describe_images.py      # Image description
│   ├── 3_build_vectordb.py       # Vector DB creation
│   ├── 4_query_engine.py         # RAG engine
│   └── 5_app.py                  # Streamlit UI
├── config/                       # Configuration
│   └── config.yaml
├── requirements.txt              # Python dependencies
└── .env                         # API keys (create this)
```

## Phase 1: Hybrid Setup (Current)

- Uses GPT-4V for image descriptions (one-time)
- Local embeddings with sentence-transformers
- Local LLM with Ollama Llama3
- ChromaDB for vector storage

**Cost**: ~$5-10 one-time for image processing

## Phase 2: Fully Local (Optional)

Transition to 100% local for complete privacy:

```bash
# Install additional dependencies
pip install -r requirements-local.txt

# Pull LLaVA model
ollama pull llava:13b

# Use local vision model
python src/2_describe_images.py --local
```

## Usage Examples

### Text Queries
- "What are the characteristics of HbE disease?"
- "Show cases with elevated HbA2"
- "Find patterns similar to HbH disease"
- "What retention times indicate beta thalassemia?"

### Image Search
1. Upload a chromatograph image
2. System describes the pattern
3. Finds similar cases in the database
4. Returns relevant patient information

## Hardware Requirements

### Phase 1 (Minimum)
- RAM: 8GB
- Storage: 5GB
- GPU: Not required

### Phase 2 (Recommended)
- RAM: 16GB+
- Storage: 15GB
- GPU: 8GB VRAM (optional)

## Troubleshooting

### Ollama not found
```bash
# Reinstall Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### Out of memory
- Reduce chunk_size in config.yaml
- Use smaller LLM model
- Close other applications

### Slow queries
- Ensure Ollama is running
- Check GPU availability
- Reduce retrieval top_k value

## Development

### Run Tests
```bash
python -m pytest tests/
```

### Update Configuration
Edit `config/config.yaml` to adjust:
- Chunk sizes
- Number of retrieval results
- LLM parameters
- Vector database settings

## License

For educational and research purposes.

## Support

For issues or questions, please refer to the implementation plan.
