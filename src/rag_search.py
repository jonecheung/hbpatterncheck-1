"""
RAG Search Module
Handles vector database search for Retrieval-Augmented Generation
"""

from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

class RAGSearchEngine:
    """Search engine for RAG using ChromaDB"""
    
    def __init__(self, persist_dir: str = None, collection_name: str = "hb_patterns"):
        """
        Initialize RAG search engine
        
        Args:
            persist_dir: Path to ChromaDB storage
            collection_name: Name of the collection
        """
        if persist_dir is None:
            project_root = Path(__file__).parent.parent
            persist_dir = str(project_root / "vector_db" / "chroma_storage")
        
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Initialize embedding model
        print("📥 Loading embedding model for RAG...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        print(f"💾 Connecting to ChromaDB at {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Connected to collection: {collection_name} ({self.collection.count()} vectors)")
        except Exception as e:
            raise Exception(f"Failed to load collection '{collection_name}': {e}")
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        min_similarity: float = 0.0
    ) -> Tuple[List[str], List[Dict], List[float]]:
        """
        Search vector database for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            Tuple of (documents, metadatas, distances)
        """
        # Embed query
        query_embedding = self.embedding_model.encode([query])
        
        # Search database
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        # Extract results
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        # Convert distances to similarity scores (cosine distance -> similarity)
        # ChromaDB uses L2 distance, convert to similarity: 1 / (1 + distance)
        similarities = [1.0 / (1.0 + d) for d in distances]
        
        # Filter by minimum similarity
        filtered_results = [
            (doc, meta, sim)
            for doc, meta, sim in zip(documents, metadatas, similarities)
            if sim >= min_similarity
        ]
        
        if filtered_results:
            documents, metadatas, similarities = zip(*filtered_results)
            documents = list(documents)
            metadatas = list(metadatas)
            similarities = list(similarities)
        else:
            documents, metadatas, similarities = [], [], []
        
        return documents, metadatas, similarities
    
    def build_context(
        self, 
        documents: List[str], 
        metadatas: List[Dict],
        similarities: List[float],
        max_length: int = 3000
    ) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            documents: Retrieved document texts
            metadatas: Document metadata
            similarities: Similarity scores
            max_length: Maximum context length in characters
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, (doc, meta, sim) in enumerate(zip(documents, metadatas, similarities), 1):
            page = meta.get('page', 'Unknown')
            
            # Format source
            source_text = f"[Source {i} - Page {page}, Relevance: {sim:.2f}]\n{doc}\n"
            
            # Check if adding this would exceed max length
            if current_length + len(source_text) > max_length:
                break
            
            context_parts.append(source_text)
            current_length += len(source_text)
        
        if not context_parts:
            return "No relevant information found in the database."
        
        context = "\n---\n\n".join(context_parts)
        return context
    
    def format_sources(
        self, 
        metadatas: List[Dict], 
        similarities: List[float]
    ) -> List[str]:
        """
        Format source citations
        
        Args:
            metadatas: Document metadata
            similarities: Similarity scores
            
        Returns:
            List of formatted source strings
        """
        sources = []
        for i, (meta, sim) in enumerate(zip(metadatas, similarities), 1):
            page = meta.get('page', 'Unknown')
            source_file = meta.get('source_file', 'Database')
            
            source_str = f"Page {page} ({source_file}) - Relevance: {sim:.0%}"
            sources.append(source_str)
        
        return sources
    
    def search_and_format(
        self, 
        query: str, 
        top_k: int = 5, 
        min_similarity: float = 0.3
    ) -> Dict:
        """
        Search and return formatted results
        
        Args:
            query: Search query
            top_k: Number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            Dict with context, sources, and metadata
        """
        # Search
        documents, metadatas, similarities = self.search(
            query, 
            top_k=top_k, 
            min_similarity=min_similarity
        )
        
        # Build context
        context = self.build_context(documents, metadatas, similarities)
        
        # Format sources
        sources = self.format_sources(metadatas, similarities)
        
        return {
            "context": context,
            "sources": sources,
            "num_results": len(documents),
            "query": query
        }


# Singleton instance (initialized once when module is imported)
_search_engine = None

def get_search_engine() -> RAGSearchEngine:
    """Get or create singleton search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = RAGSearchEngine()
    return _search_engine


# Test function
def test_rag_search():
    """Test RAG search functionality"""
    print("=" * 70)
    print("Testing RAG Search Engine")
    print("=" * 70)
    
    # Initialize
    engine = RAGSearchEngine()
    
    # Test queries
    test_queries = [
        "What is HbE disease?",
        "Beta thalassemia patterns",
        "Elevated HbA2",
        "Constant Spring variant"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 70)
        
        result = engine.search_and_format(query, top_k=3, min_similarity=0.3)
        
        print(f"📊 Found {result['num_results']} results\n")
        
        print("📚 Sources:")
        for source in result['sources']:
            print(f"  - {source}")
        
        print(f"\n📝 Context preview (first 200 chars):")
        print(result['context'][:200] + "...")
        print()


if __name__ == "__main__":
    test_rag_search()

