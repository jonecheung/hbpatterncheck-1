"""
Visual Search Module
Handles image upload, CLIP embedding, and similarity search
Supports both images (PNG, JPG) and PDF files
"""

import open_clip
import torch
from PIL import Image
import chromadb
import os
from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Tuple
import io
import fitz  # PyMuPDF
import pytesseract
from peak_analyzer import get_peak_analyzer
import base64
import asyncio
from openrouter_client import OpenRouterClient

class VisualSearchEngine:
    """Visual similarity search using CLIP embeddings"""
    
    def __init__(self, persist_dir: str = None, collection_name: str = "hb_image_embeddings"):
        """
        Initialize visual search engine
        
        Args:
            persist_dir: Path to ChromaDB storage
            collection_name: Name of image embeddings collection
        """
        if persist_dir is None:
            project_root = Path(__file__).parent.parent
            persist_dir = str(project_root / "vector_db" / "chroma_storage")
        
        # Initialize CLIP model
        print("📥 Loading CLIP model for visual search...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32',
            pretrained='openai'
        )
        self.model.eval()
        
        # Use Apple Silicon GPU if available
        if torch.backends.mps.is_available():
            self.device = 'mps'
        elif torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
        
        # Initialize OpenRouter client for LLM screening
        self.openrouter_client = OpenRouterClient()
        
        self.model.to(self.device)
        
        # Initialize peak analyzer
        print("🔬 Loading peak analyzer...")
        self.peak_analyzer = get_peak_analyzer()
        print("✅ Peak analyzer ready!")
        
        # Initialize LLM client (OpenRouter via OpenAI SDK)
        self.llm_client = None
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                self.llm_client = OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1")
                print("✅ LLM client ready (OpenRouter)")
            except Exception as e:
                print(f"⚠️ Failed to init LLM client: {e}")
        
        # Initialize ChromaDB
        print(f"💾 Connecting to ChromaDB at {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Connected to collection: {collection_name} ({self.collection.count()} images)")
        except Exception as e:
            raise Exception(f"Failed to load collection '{collection_name}': {e}")
    
    def detect_system_type(self, image: Image.Image) -> str:
        """
        Detect chromatograph system type from image header
        
        Args:
            image: PIL Image
            
        Returns:
            'biorad', 'sebia', or 'unknown'
        """
        try:
            # Extract top 250 pixels for OCR
            width, height = image.size
            header_region = image.crop((0, 0, width, min(250, height)))
            
            # OCR text extraction
            text = pytesseract.image_to_string(header_region).upper()
            
            # Detect system type
            if 'BIO-RAD' in text or 'BIORAD' in text or 'CDM' in text:
                return 'biorad'
            elif 'SEBIA' in text or 'CAPILLARYS' in text or 'CAPILLARY' in text:
                return 'sebia'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def crop_chromatograph(self, image: Image.Image) -> Image.Image:
        """
        Smart crop chromatograph based on system type
        
        Args:
            image: PIL Image (full page)
            
        Returns:
            Cropped PIL Image (chromatograph only)
        """
        system_type = self.detect_system_type(image)
        width, height = image.size
        
        if system_type == 'biorad':
            # Bio-Rad CDM: Bottom 60%
            y_start = int(height * 0.4)
            cropped = image.crop((0, y_start, width, height))
        elif system_type == 'sebia':
            # Sebia: Middle 70%
            y_start = int(height * 0.15)
            y_end = int(height * 0.85)
            cropped = image.crop((0, y_start, width, y_end))
        else:
            # Unknown: Bottom 60% (fallback)
            y_start = int(height * 0.4)
            cropped = image.crop((0, y_start, width, height))
        
        return cropped
    
    def extract_from_pdf(self, pdf_bytes: bytes) -> Image.Image:
        """
        Extract and crop chromatograph from PDF
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Cropped chromatograph image
        """
        # Open PDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Get first page (most PDFs have chromatograph on page 1 or 2)
        page = doc[0]
        
        # Render at high resolution
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        
        doc.close()
        
        # Crop chromatograph region
        cropped = self.crop_chromatograph(image)
        
        return cropped
    
    def embed_image(self, image: Image.Image) -> List[float]:
        """
        Generate CLIP embedding for an image
        
        Args:
            image: PIL Image
            
        Returns:
            List of floats (512-dim embedding)
        """
        # Preprocess image
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            embedding = self.model.encode_image(image_input)
            # Normalize
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            # Convert to list
            embedding_list = embedding.cpu().numpy()[0].tolist()
        
        return embedding_list
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    
    async def llm_compare_chromatographs(self, query_image: Image.Image, candidate_image: Image.Image) -> bool:
        """
        Use LLM vision model to compare two chromatographs
        
        Args:
            query_image: Query chromatograph (PIL Image)
            candidate_image: Candidate chromatograph (PIL Image)
            
        Returns:
            True if LLM says they are clinically similar, False otherwise
        """
        # Encode images to base64
        query_b64 = self._image_to_base64(query_image)
        candidate_b64 = self._image_to_base64(candidate_image)
        
        # Create comparison prompt
        prompt = """You are a clinical laboratory expert analyzing hemoglobin chromatographs.

I will show you TWO chromatograph images (QUERY and CANDIDATE).

Your task: Determine if these two chromatographs are clinically SIMILAR enough to be helpful for diagnosis.

Focus on:
1. **A2 peak height** (usually 2nd peak): Are they comparable? (e.g., both small, or both large)
2. **F peak height** (if present): Are they similar?
3. **Overall pattern**: Do they show the same general hemoglobin pattern?

**IMPORTANT RULES:**
- If the A2 peak is VERY DIFFERENT (e.g., one tiny, one huge), say NO
- If the overall pattern is clearly different, say NO
- Small variations are OK, but major differences are NOT

**Answer with ONLY ONE WORD: YES or NO**

First image is the QUERY (what user uploaded).
Second image is the CANDIDATE (from our database)."""
        
        # Build messages with both images
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{query_b64}"}},
                    {"type": "text", "text": "↑ QUERY image (user uploaded)"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{candidate_b64}"}},
                    {"type": "text", "text": "↑ CANDIDATE image (from database)\n\nAre these clinically similar? Answer YES or NO only:"}
                ]
            }
        ]
        
        # Call OpenRouter vision API
        try:
            payload = {
                "model": "openai/gpt-4o",  # GPT-4o supports multiple images
                "messages": messages,
                "max_tokens": 10,
                "temperature": 0.3  # Low temperature for consistent YES/NO
            }
            
            async with asyncio.timeout(30):
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.openrouter_client.base_url}/chat/completions",
                        headers=self.openrouter_client._get_headers(),
                        json=payload
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    llm_response = data["choices"][0]["message"]["content"].strip().upper()
                    
                    # Parse YES/NO
                    if "YES" in llm_response:
                        return True
                    else:
                        return False
                    
        except Exception as e:
            print(f"   ⚠️ LLM screening failed: {e}, defaulting to ACCEPT")
            return True  # If LLM fails, don't filter out (permissive fallback)
    
    def search_similar(
        self,
        image: Image.Image = None,
        pdf_bytes: bytes = None,
        top_k: int = 10,
        category_filter: str = None
    ) -> Tuple[List[Dict], List[float]]:
        """
        Search for visually similar chromatographs
        
        Args:
            image: PIL Image to search for (for image uploads)
            pdf_bytes: PDF file bytes (for PDF uploads)
            top_k: Number of results to return
            category_filter: Optional category to filter by (e.g., 'hb_e')
            
        Returns:
            Tuple of (results, similarities)
        """
        # Handle PDF input
        if pdf_bytes is not None:
            print("📄 Processing PDF...")
            image = self.extract_from_pdf(pdf_bytes)
            print(f"✅ Extracted and cropped chromatograph from PDF")
        
        # Handle image input (crop if it looks like a full page)
        elif image is not None:
            # If image is large (likely a full page), try to crop
            width, height = image.size
            if height > 800:  # Likely a full page scan
                print("📸 Cropping chromatograph from image...")
                image = self.crop_chromatograph(image)
                print(f"✅ Cropped to chromatograph region")
        else:
            raise ValueError("Must provide either image or pdf_bytes")
        
        # Embed query image
        query_embedding = self.embed_image(image)
        
        # Prepare search parameters
        search_kwargs = {
            'query_embeddings': [query_embedding],
            'n_results': top_k
        }
        
        # Add category filter if specified
        if category_filter:
            search_kwargs['where'] = {'category': category_filter}
        
        # Search vector database
        results = self.collection.query(**search_kwargs)
        
        # Extract and format results
        formatted_results = []
        similarities = []
        
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                result_id = results['ids'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Convert distance to similarity (cosine similarity for ChromaDB)
                # ChromaDB uses L2 distance by default, but we set cosine in collection
                # For cosine: distance is actually 1 - similarity, so similarity = 1 - distance
                # But since we normalized embeddings, let's use 1/(1+distance) for safety
                similarity = 1.0 / (1.0 + distance)
                
                formatted_results.append({
                    'id': result_id,
                    'category': metadata.get('category', 'unknown'),
                    'source': metadata.get('source', 'unknown'),
                    'system_type': metadata.get('system_type', 'unknown'),
                    'image_file': metadata.get('image_file', ''),
                    'page': metadata.get('page', 0),
                    'original_file': metadata.get('original_file', ''),
                    'similarity': similarity
                })
                
                similarities.append(similarity)
        
        return formatted_results, similarities
    
    async def search_similar_with_peaks(
        self,
        image: Image.Image = None,
        pdf_bytes: bytes = None,
        top_k: int = 10,
        clip_weight: float = 0.6,
        peak_weight: float = 0.4,
        category_filter: str = None,
        llm_screen: bool = False
    ) -> Tuple[List[Dict], List[float], Dict]:
        """
        Search with hybrid CLIP + peak-based similarity
        
        Args:
            image: PIL Image to search for
            pdf_bytes: PDF file bytes
            top_k: Number of results
            clip_weight: Weight for CLIP similarity (0-1)
            peak_weight: Weight for peak similarity (0-1)
            category_filter: Optional category filter
            
        Returns:
            Tuple of (results, hybrid_scores, query_features)
        """
        # Get initial CLIP-based results (fetch more for re-ranking)
        initial_results, clip_similarities = self.search_similar(
            image=image,
            pdf_bytes=pdf_bytes,
            top_k=top_k * 3,  # Get 3x results for re-ranking
            category_filter=category_filter
        )
        
        # Handle PDF/image input
        if pdf_bytes is not None:
            query_image = self.extract_from_pdf(pdf_bytes)
        elif image is not None:
            width, height = image.size
            if height > 800:
                query_image = self.crop_chromatograph(image)
            else:
                query_image = image
        
        # Analyze query image peaks
        print("🔬 Analyzing query chromatograph peaks...")
        query_features = self.peak_analyzer.analyze_image(query_image)
        print(f"   Found {query_features['num_peaks']} peaks in query | heights={query_features.get('heights')} | A2={query_features.get('a2_concentration')} | F={query_features.get('f_concentration')}")
        
        # Re-rank with peak similarity
        print("🔄 Re-ranking with peak-based similarity...")
        hybrid_results = []
        
        for result, clip_sim in zip(initial_results, clip_similarities):
            # Load result image
            image_file = result['image_file']
            
            # Determine image path
            if result['source'] == 'main_database':
                img_path = Path(__file__).parent.parent / "data" / "cropped_images_main" / image_file.replace('main_', '')
            else:
                img_path = Path(__file__).parent.parent / "data" / "cropped_images_reference" / image_file.replace('reference_', '')
            
            try:
                # Load and analyze result image
                result_image = Image.open(img_path)
                result_features = self.peak_analyzer.analyze_image(result_image)
                
                # STEP 1: Permissive filter (catch only extreme outliers)
                # Let most results through - Step 2 will do strict F%/A2% filtering
                is_similar, reason = self.peak_analyzer.is_clinically_similar(
                    query_features,
                    result_features,
                    max_concentration_ratio=10.0,  # Very permissive (Step 2 will filter)
                    max_peak_count_diff=5  # Allow larger peak count differences
                )
                
                if not is_similar:
                    # Skip this result - too different to show
                    print(f"   ⚠️  Filtered out {image_file}: {reason}")
                    continue
                
                # Calculate peak similarity
                peak_sim, peak_details = self.peak_analyzer.calculate_peak_similarity(
                    query_features,
                    result_features
                )
                
                # Calculate hybrid score
                hybrid_score = (clip_weight * clip_sim) + (peak_weight * peak_sim)
                
                # Add to results
                result_with_scores = {
                    **result,
                    'clip_similarity': clip_sim,
                    'peak_similarity': peak_sim,
                    'hybrid_similarity': hybrid_score,
                    'peak_details': peak_details,
                    'num_peaks': result_features['num_peaks']
                }
                
                hybrid_results.append((result_with_scores, hybrid_score))
                
            except Exception as e:
                # If peak analysis fails, use CLIP score only
                print(f"   ⚠️ Peak analysis failed for {image_file}: {e}")
                result_with_scores = {
                    **result,
                    'clip_similarity': clip_sim,
                    'peak_similarity': None,
                    'hybrid_similarity': clip_sim,
                    'num_peaks': None
                }
                hybrid_results.append((result_with_scores, clip_sim))
        
        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        
        # STEP 2: LLM Vision Screening (if enabled)
        if llm_screen:
            print("🤖 STEP 2: Applying LLM vision screening...")
            filtered_results = []
            
            # Screen top 2x results with LLM
            try:
                tasks = []
                for result, score in hybrid_results[:top_k * 2]:  # Screen top 2x results
                    # Load result image
                    image_file = result['image_file']
                    if result['source'] == 'main_database':
                        img_path = Path(__file__).parent.parent / "data" / "cropped_images_main" / image_file.replace('main_', '')
                    else:
                        img_path = Path(__file__).parent.parent / "data" / "cropped_images_reference" / image_file.replace('reference_', '')
                    
                    try:
                        result_image = Image.open(img_path)
                        # Create task for LLM comparison
                        task = self.llm_compare_chromatographs(query_image, result_image)
                        tasks.append((result, score, task, image_file))
                    except Exception as e:
                        print(f"   ⚠️ Failed to load {image_file}: {e}")
                        continue
                
                # Run all comparisons in parallel using asyncio.gather
                results_to_process = await asyncio.gather(*[task for _, _, task, _ in tasks], return_exceptions=True)
                
                # Process results
                for i, (result, score, _, image_file) in enumerate(tasks):
                    try:
                        is_similar = results_to_process[i]
                        if isinstance(is_similar, Exception):
                            print(f"   ⚠️ LLM screening failed for {image_file}: {is_similar}, keeping result")
                            filtered_results.append((result, score))
                        elif is_similar:
                            print(f"   ✅ LLM APPROVED: {image_file}")
                            filtered_results.append((result, score))
                        else:
                            print(f"   ❌ LLM REJECTED: {image_file}")
                    except Exception as e:
                        print(f"   ⚠️ Processing failed for {image_file}: {e}, keeping result")
                        filtered_results.append((result, score))
                
            except Exception as e:
                print(f"   ⚠️ LLM screening failed: {e}, using all results")
                filtered_results = hybrid_results
            
            # Take top-k from LLM-approved results
            top_results = filtered_results[:top_k]
            final_results = [r[0] for r in top_results]
            final_scores = [r[1] for r in top_results]
            
            print(f"✅ Re-ranked {len(initial_results)} → LLM screened {len(hybrid_results)} → Approved {len(filtered_results)} → Final {len(final_results)}")
        
        else:
            # No LLM screening - just take top-k
            print("⏭️  Skipping LLM screening (disabled)")
            top_results = hybrid_results[:top_k]
            final_results = [r[0] for r in top_results]
            final_scores = [r[1] for r in top_results]
            
            print(f"✅ Re-ranked {len(initial_results)} → Final {len(final_results)}")
        
        return final_results, final_scores, query_features
    
    def format_search_results(
        self,
        results: List[Dict],
        similarities: List[float]
    ) -> List[str]:
        """
        Format search results as human-readable strings
        
        Args:
            results: List of result dictionaries
            similarities: List of similarity scores
            
        Returns:
            List of formatted strings
        """
        formatted = []
        
        for i, (result, sim) in enumerate(zip(results, similarities), 1):
            category = result['category'].replace('_', ' ').title()
            source = result['source']
            system = result['system_type'].replace('_', ' ').title()
            
            formatted_str = (
                f"Rank #{i}: {category} "
                f"(Similarity: {sim:.1%}, "
                f"System: {system}, "
                f"Source: {source})"
            )
            
            formatted.append(formatted_str)
        
        return formatted


# Singleton instance
_visual_search_engine = None

def get_visual_search_engine() -> VisualSearchEngine:
    """Get or create singleton visual search engine instance"""
    global _visual_search_engine
    if _visual_search_engine is None:
        _visual_search_engine = VisualSearchEngine()
    return _visual_search_engine

