"""
Test vector database retrieval
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, get_project_root
import chromadb


def test_vectordb_exists():
    """Test if vector database exists"""
    config = load_config()
    project_root = get_project_root()
    persist_dir = project_root / config['vectordb']['persist_directory']
    
    if persist_dir.exists():
        print(f"✅ Vector DB directory exists: {persist_dir}")
        return True
    else:
        print(f"⚠️  Vector DB not found. Run: python src/3_build_vectordb.py")
        return False


def test_vectordb_connection():
    """Test connection to vector database"""
    config = load_config()
    project_root = get_project_root()
    persist_dir = project_root / config['vectordb']['persist_directory']
    
    try:
        client = chromadb.PersistentClient(path=str(persist_dir))
        collection = client.get_collection(name=config['vectordb']['collection_name'])
        
        count = collection.count()
        print(f"✅ Connected to vector database")
        print(f"   Collection: {config['vectordb']['collection_name']}")
        print(f"   Vector count: {count}")
        
        return count > 0
    except Exception as e:
        print(f"❌ Error connecting to vector DB: {e}")
        return False


def test_similarity_search():
    """Test similarity search"""
    config = load_config()
    project_root = get_project_root()
    persist_dir = project_root / config['vectordb']['persist_directory']
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model
        model = SentenceTransformer(config['embeddings']['model'])
        
        # Connect to DB
        client = chromadb.PersistentClient(path=str(persist_dir))
        collection = client.get_collection(name=config['vectordb']['collection_name'])
        
        # Test query
        test_query = "What are hemoglobin pattern abnormalities?"
        query_embedding = model.encode(test_query).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            print(f"✅ Similarity search working")
            print(f"   Query: {test_query}")
            print(f"   Results found: {len(results['documents'][0])}")
            return True
        else:
            print(f"⚠️  No results found for test query")
            return False
            
    except Exception as e:
        print(f"❌ Error during similarity search: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Vector Database Retrieval")
    print("=" * 60)
    
    if test_vectordb_exists():
        test_vectordb_connection()
        test_similarity_search()
    
    print("\n✅ Retrieval tests complete!")

