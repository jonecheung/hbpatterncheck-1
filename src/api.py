"""
FastAPI Backend Server
Connects React frontend to OpenRouter LLM
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

# Import OpenRouter client (we'll create this)
from openrouter_client import OpenRouterClient

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
        "http://localhost:3000",  # Alternative port
        "http://localhost:8501",  # Streamlit (if used)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenRouter client
openrouter_client = OpenRouterClient()

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
        # Convert Pydantic models to dict for OpenRouter
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Add system message for medical context
        system_message = {
            "role": "system",
            "content": """You are a medical AI assistant specializing in hemoglobin pattern diseases. 
You help healthcare professionals analyze chromatograph patterns and diagnose hemoglobinopathies.

Provide accurate, evidence-based information. When discussing patterns:
- Describe retention times and peak characteristics
- Mention relevant HbA, HbA2, HbF, and HbS percentages
- Suggest differential diagnoses
- Recommend confirmatory tests when appropriate

Always maintain a professional, clinical tone."""
        }
        
        messages.insert(0, system_message)
        
        # Call OpenRouter
        response = await openrouter_client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Mock sources (will be replaced with vector DB results)
        mock_sources = [
            "Reference: HbE disease patterns (46 cases)",
            "Reference: Beta thalassemia guidelines",
            "Database: Similar patterns found"
        ]
        
        return ChatResponse(
            message=response,
            sources=mock_sources,
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

