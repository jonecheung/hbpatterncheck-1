"""
Build Vector Database
Creates ChromaDB with embeddings from extracted PDF text
"""

import json
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import sys

def load_text_data(text_file: Path) -> List[Dict]:
    """Load extracted text from JSON"""
    print(f"📄 Loading text from: {text_file}")
    with open(text_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} pages")
    return data

def chunk_text(text_data: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """
    Chunk text data into smaller pieces
    Simple character-based chunking with overlap
    """
    print(f"\n📝 Chunking text (size={chunk_size}, overlap={chunk_overlap})...")
    
    chunks = []
    for page_data in text_data:
        page_num = page_data['page']
        text = page_data['text']
        
        # Skip empty pages
        if not text.strip():
            continue
        
        # Simple chunking by character count
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Get chunk
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Only add if chunk has meaningful content
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text.strip(),
                    'metadata': {
                        'type': 'text',
                        'page': page_num,
                        'chunk_index': chunk_index,
                        'source_file': 'Abnormal Hb Pattern(pdf).pdf',
                        'char_start': start,
                        'char_end': end
                    }
                })
                chunk_index += 1
            
            # Move start forward (with overlap)
            start = end - chunk_overlap
    
    print(f"✅ Created {len(chunks)} text chunks")
    return chunks

def build_vector_database(chunks: List[Dict], persist_dir: str, collection_name: str):
    """
    Build ChromaDB vector database with embeddings
    """
    print("\n🔧 Building vector database...")
    
    # Initialize embedding model
    print(f"📥 Loading embedding model: sentence-transformers/all-MiniLM-L6-v2")
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print(f"✅ Model loaded (384 dimensions)")
    
    # Initialize ChromaDB
    persist_path = Path(persist_dir)
    persist_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Initializing ChromaDB at {persist_path}")
    client = chromadb.PersistentClient(path=str(persist_path))
    
    # Delete collection if it exists (fresh start)
    try:
        client.delete_collection(name=collection_name)
        print(f"🗑️  Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Hemoglobin pattern disease database"}
    )
    print(f"✅ Created collection: {collection_name}")
    
    # Process documents in batches
    print(f"\n🔄 Generating embeddings and adding to database...")
    print(f"   Processing {len(chunks)} chunks...")
    
    batch_size = 50
    for i in tqdm(range(0, len(chunks), batch_size), desc="Building DB"):
        batch = chunks[i:i + batch_size]
        
        # Prepare batch data
        texts = [chunk['text'] for chunk in batch]
        metadatas = [chunk['metadata'] for chunk in batch]
        ids = [f"doc_{i + j}" for j in range(len(batch))]
        
        # Generate embeddings
        embeddings = embedding_model.encode(texts, show_progress_bar=False)
        embeddings_list = embeddings.tolist()
        
        # Add to collection
        collection.add(
            documents=texts,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
    
    print(f"\n✅ Successfully added {len(chunks)} documents to vector database")
    
    # Verify
    count = collection.count()
    print(f"📊 Database contains {count} vectors")
    
    return collection

def test_database(persist_dir: str, collection_name: str):
    """Test the database with a sample query"""
    print("\n🧪 Testing database with sample query...")
    
    # Load database
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_collection(name=collection_name)
    
    # Load embedding model
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Test query
    test_query = "What is HbE disease?"
    print(f"   Query: '{test_query}'")
    
    # Embed query
    query_embedding = embedding_model.encode([test_query])
    
    # Search
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=3
    )
    
    print(f"\n✅ Found {len(results['documents'][0])} results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        page = metadata['page']
        preview = doc[:100] + "..." if len(doc) > 100 else doc
        print(f"\n   [{i}] Page {page}:")
        print(f"       {preview}")
    
    return True

def main():
    """Main vector database building pipeline"""
    print("=" * 70)
    print("HB Pattern Vector Database Builder")
    print("=" * 70)
    
    # Paths
    project_root = Path(__file__).parent.parent
    text_file = project_root / "data" / "pdf_text.json"
    persist_dir = project_root / "vector_db" / "chroma_storage"
    collection_name = "hb_patterns"
    
    # Check if text data exists
    if not text_file.exists():
        print(f"❌ Error: Text data not found at {text_file}")
        print("Please extract PDF text first")
        sys.exit(1)
    
    try:
        # Step 1: Load data
        print("\n--- Step 1: Loading Data ---")
        text_data = load_text_data(text_file)
        
        # Step 2: Chunk text
        print("\n--- Step 2: Chunking Text ---")
        chunks = chunk_text(text_data, chunk_size=1000, chunk_overlap=200)
        
        # Step 3: Build vector database
        print("\n--- Step 3: Building Vector Database ---")
        collection = build_vector_database(chunks, str(persist_dir), collection_name)
        
        # Step 4: Test database
        print("\n--- Step 4: Testing Database ---")
        test_database(str(persist_dir), collection_name)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Vector Database Summary")
        print("=" * 70)
        print(f"✅ Collection name: {collection_name}")
        print(f"✅ Persist directory: {persist_dir}")
        print(f"✅ Total vectors: {collection.count()}")
        print(f"✅ Embedding model: sentence-transformers/all-MiniLM-L6-v2")
        print(f"✅ Vector dimension: 384")
        print(f"✅ Source pages: {len(text_data)}")
        print(f"✅ Text chunks: {len(chunks)}")
        
        print("\n✅ Vector database build complete!")
        print("\n🎉 Ready for RAG queries!")
        print("\nNext step: Update API to use vector database for search")
        
    except Exception as e:
        print(f"\n❌ Error building database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

