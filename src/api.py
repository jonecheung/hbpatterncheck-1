"""
FastAPI Backend Server
Connects React frontend to OpenRouter LLM
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import base64
from pathlib import Path
import io
from PIL import Image

# Load environment variables
load_dotenv()

# Import OpenRouter client and RAG search
from openrouter_client import OpenRouterClient
from rag_search import get_search_engine
from visual_search import get_visual_search_engine

# Initialize FastAPI app
app = FastAPI(
    title="Hemoglobin Pattern Chatbot API",
    description="Backend API for HB Pattern analysis",
    version="1.0.0"
)

# Configure CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Vite alternative port
        "http://localhost:8081",  # Vite alternative port
        "http://localhost:8888",  # Test page server
        "http://localhost:3000",  # React default
        "http://localhost:8501",  # Streamlit (if used)
        "null",  # Allow file:// URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenRouter client
openrouter_client = OpenRouterClient()

# Initialize RAG search engine
print("🔍 Initializing RAG search engine...")
try:
    rag_engine = get_search_engine()
    print("✅ RAG search engine ready!")
except Exception as e:
    print(f"⚠️  Warning: RAG search not available: {e}")
    rag_engine = None

# Initialize Visual search engine
print("🎨 Initializing Visual search engine...")
try:
    visual_engine = get_visual_search_engine()
    print("✅ Visual search engine ready!")
except Exception as e:
    print(f"⚠️  Warning: Visual search not available: {e}")
    visual_engine = None

# Request/Response models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "meta-llama/llama-3.1-8b-instruct"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[str]] = []
    model_used: str

class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: Optional[str] = "Analyze this hemoglobin chromatograph pattern"

class ImageAnalysisResponse(BaseModel):
    analysis: str
    pattern_type: Optional[str] = None
    confidence: Optional[float] = None
    sources: Optional[List[str]] = []

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HB Pattern Chatbot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "api_version": "1.0.0"
    }

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages
    
    This endpoint:
    1. Receives chat history from frontend
    2. Sends to OpenRouter LLM
    3. Returns AI response
    """
    try:
        # Get user's last message for RAG search
        user_query = request.messages[-1].content if request.messages else ""
        
        # Convert Pydantic models to dict for OpenRouter
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Search vector database for relevant context (RAG)
        context = ""
        sources = []
        
        if rag_engine and user_query:
            print(f"🔍 Searching database for: '{user_query[:50]}...'")
            rag_results = rag_engine.search_and_format(
                query=user_query,
                top_k=5,
                min_similarity=0.3
            )
            
            context = rag_results['context']
            sources = rag_results['sources']
            print(f"✅ Found {rag_results['num_results']} relevant cases")
        
        # Build enhanced system message with context
        if context and context != "No relevant information found in the database.":
            system_content = f"""You are a medical AI assistant specializing in hemoglobin pattern diseases. 
You help healthcare professionals analyze chromatograph patterns and diagnose hemoglobinopathies.

IMPORTANT: Use the following information from the patient database to answer the question:

{context}

Based on this database information:
- Provide specific, evidence-based answers
- Cite page numbers when referencing specific cases
- Describe retention times and peak characteristics
- Mention relevant HbA, HbA2, HbF, and HbS percentages
- Suggest differential diagnoses
- Recommend confirmatory tests when appropriate

Always maintain a professional, clinical tone and reference the source pages."""
        else:
            # No relevant context found, use general knowledge
            system_content = """You are a medical AI assistant specializing in hemoglobin pattern diseases. 
You help healthcare professionals analyze chromatograph patterns and diagnose hemoglobinopathies.

Note: No specific cases were found in the database for this query. Provide general medical knowledge.

When discussing patterns:
- Describe retention times and peak characteristics
- Mention relevant HbA, HbA2, HbF, and HbS percentages
- Suggest differential diagnoses
- Recommend confirmatory tests when appropriate

Always maintain a professional, clinical tone."""
            sources = ["General medical knowledge (no specific database matches)"]
        
        system_message = {
            "role": "system",
            "content": system_content
        }
        
        messages.insert(0, system_message)
        
        # Call OpenRouter with context
        response = await openrouter_client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            message=response,
            sources=sources,
            model_used=request.model
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# Image upload endpoint
@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Handle image upload
    
    This endpoint:
    1. Receives chromatograph image from frontend
    2. Converts to base64
    3. Returns file info for further processing
    """
    try:
        # Read file contents
        contents = await file.read()
        
        # Convert to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        return {
            "success": True,
            "filename": file.filename,
            "size": len(contents),
            "base64": base64_image[:100] + "...",  # Preview only
            "message": "Image uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

# Image analysis endpoint
@app.post("/api/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze chromatograph image using Vision API
    
    This endpoint:
    1. Receives base64 image
    2. Sends to OpenRouter Vision model (GPT-4V)
    3. Returns pattern analysis
    """
    try:
        # Create specialized prompt for chromatograph analysis
        analysis_prompt = f"""Analyze this hemoglobin chromatograph image in detail:

1. Identify all visible peaks and their approximate retention times
2. Estimate relative peak heights/percentages
3. Describe the overall pattern characteristics
4. Suggest possible hemoglobin variants or conditions
5. Note any abnormal features

{request.prompt}

Provide a technical, clinical analysis suitable for medical professionals."""
        
        # Call OpenRouter Vision API
        analysis = await openrouter_client.analyze_image(
            image_base64=request.image_base64,
            prompt=analysis_prompt
        )
        
        # Parse analysis to extract pattern type (simplified)
        pattern_type = "Unknown"
        if "HbE" in analysis:
            pattern_type = "HbE Disease"
        elif "beta" in analysis.lower() and "thal" in analysis.lower():
            pattern_type = "Beta Thalassemia"
        elif "HbS" in analysis:
            pattern_type = "Sickle Cell"
        
        # Mock sources (will be replaced with similar pattern search)
        mock_sources = [
            "Similar to: hb_e reference case #23",
            "Pattern matches: 3 database cases",
            "Confidence: High (85%)"
        ]
        
        return ImageAnalysisResponse(
            analysis=analysis,
            pattern_type=pattern_type,
            confidence=0.85,
            sources=mock_sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# Get reference categories endpoint
@app.get("/api/references")
async def get_references():
    """
    Get list of reference chromatograph categories
    """
    try:
        base_path = Path(__file__).parent.parent / "data" / "reference_chromatographs"
        
        categories = []
        if base_path.exists():
            for folder in sorted(base_path.iterdir()):
                if folder.is_dir() and not folder.name.startswith('.'):
                    pdf_count = len(list(folder.glob("*.pdf")))
                    categories.append({
                        "name": folder.name,
                        "display_name": folder.name.replace("_", " ").title(),
                        "count": pdf_count
                    })
        
        return {
            "categories": categories,
            "total_count": sum(c["count"] for c in categories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"References error: {str(e)}")

# Search endpoint (for future vector DB integration)
@app.post("/api/search")
async def search(query: str, top_k: int = 5):
    """
    Search vector database for relevant cases
    
    This will be implemented when vector DB is ready
    """
    return {
        "query": query,
        "results": [],
        "message": "Vector database search - coming soon!"
    }

# Image serving endpoints
@app.get("/api/images/main/{filename}")
async def get_main_image(filename: str):
    """
    Serve images from main database (Abnormal Hb Pattern PDF)
    
    Args:
        filename: Image filename (e.g., page_21_full.png)
    
    Returns:
        PNG image file
    """
    try:
        # Security: validate filename (no path traversal)
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Build path to image
        image_path = Path(__file__).parent.parent / "data" / "extracted_images" / filename
        
        # Check if file exists
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        # Check if it's actually a file (not a directory)
        if not image_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Serve the image
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

@app.get("/api/images/reference/{filename}")
async def get_reference_image(filename: str):
    """
    Serve images from reference chromatographs
    
    Args:
        filename: Image filename (e.g., hb_e_2022_08_18-..._page1.png)
    
    Returns:
        PNG image file
    """
    try:
        # Security: validate filename (no path traversal)
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Build path to image
        image_path = Path(__file__).parent.parent / "data" / "reference_images" / filename
        
        # Check if file exists
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        # Check if it's actually a file
        if not image_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Serve the image
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

# Visual search endpoint
@app.post("/api/visual-search")
async def visual_search(
    file: UploadFile = File(...), 
    top_k: int = 10,
    llm_screen: bool = True,  # Enable LLM screening by default
    page_number: int = 0  # Which page to extract from PDF (0-indexed)
):
    """
    Visual similarity search - upload chromatograph image or PDF to find similar patterns
    
    Args:
        file: Uploaded image file (PNG, JPG) or PDF
        top_k: Number of similar images to return
        llm_screen: Enable LLM vision screening to filter bad results (default: True)
        page_number: Which page to extract from PDF (0 = first page, 1 = second page, etc.)
    
    Returns:
        JSON with similar images and metadata
    """
    try:
        if not visual_engine:
            raise HTTPException(status_code=503, detail="Visual search not available")
        
        # Read uploaded file
        contents = await file.read()
        
        # Detect file type
        is_pdf = file.filename.lower().endswith('.pdf') or contents[:4] == b'%PDF'
        
        # Hybrid search with LLM screening:
        # Step 1: CLIP + peak-based similarity search
        # Step 2: LLM vision model screens results (if enabled)
        #   - LLM looks at both images and filters out clinically dissimilar ones
        #   - No OCR needed - LLM directly sees the chromatograph patterns
        if is_pdf:
            results, similarities, query_features = await visual_engine.search_similar_with_peaks(
                pdf_bytes=contents, 
                top_k=top_k,
                clip_weight=0.40,  # 40% Visual similarity
                peak_weight=0.60,  # 60% Clinical features (balanced)
                llm_screen=llm_screen,
                page_number=page_number
            )
        else:
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            results, similarities, query_features = await visual_engine.search_similar_with_peaks(
                image=image, 
                top_k=top_k,
                clip_weight=0.40,  # 40% Visual
                peak_weight=0.60,  # 60% Clinical
                llm_screen=llm_screen,
                page_number=page_number  # Ignored for image uploads
            )
        
        # Format results
        formatted_results = []
        for result in results:
            # Build image URL
            if result['source'] == 'main_database':
                image_url = f"/api/images/main/{result['image_file'].replace('main_cropped_', '')}"
            else:
                image_url = f"/api/images/reference/{result['image_file'].replace('reference_cropped_', '')}"
            
            formatted_results.append({
                'category': result['category'],
                'similarity': result.get('hybrid_similarity', result.get('similarity', 0)),
                'clip_similarity': result.get('clip_similarity'),
                'peak_similarity': result.get('peak_similarity'),
                'num_peaks': result.get('num_peaks'),
                'peak_details': result.get('peak_details'),
                'system_type': result['system_type'],
                'source': result['source'],
                'image_url': image_url,
                'original_file': result.get('original_file', '')
            })
        
        return {
            'results': formatted_results,
            'total': len(formatted_results),
            'query_image': file.filename,
            'query_features': {
                'num_peaks': query_features.get('num_peaks', 0),
                'peak_positions': query_features.get('normalized_positions', [])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run server
    print("🚀 Starting Hemoglobin Pattern Chatbot API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 Docs available at: http://localhost:8000/docs")
    print("🔗 Frontend should connect to: http://localhost:8000")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

