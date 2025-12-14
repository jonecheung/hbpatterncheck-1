"""
Build Vector Database with both Text and Image Embeddings
Creates separate collections for text (384-dim) and images (512-dim)
"""

import chromadb
from chromadb.config import Settings
import json
from pathlib import Path
from tqdm import tqdm

def load_text_data():
    """Load text data from PDF extraction"""
    project_root = Path(__file__).parent.parent
    text_file = project_root / "data" / "pdf_text.json"
    
    if not text_file.exists():
        print("⚠️  Text data not found, skipping text collection")
        return None
    
    with open(text_file, 'r') as f:
        text_data = json.load(f)
    
    return text_data

def load_image_embeddings():
    """Load CLIP image embeddings"""
    project_root = Path(__file__).parent.parent
    
    # Load both main and reference embeddings
    main_file = project_root / "data" / "clip_embeddings_main.json"
    ref_file = project_root / "data" / "clip_embeddings_reference.json"
    
    embeddings = {}
    
    if main_file.exists():
        with open(main_file, 'r') as f:
            main_emb = json.load(f)
        embeddings.update({f"main_{k}": v for k, v in main_emb.items()})
    
    if ref_file.exists():
        with open(ref_file, 'r') as f:
            ref_emb = json.load(f)
        embeddings.update({f"reference_{k}": v for k, v in ref_emb.items()})
    
    return embeddings

def load_crop_metadata():
    """Load cropping metadata to get page numbers and categories"""
    project_root = Path(__file__).parent.parent
    
    metadata = {}
    
    # Load main metadata
    main_meta_file = project_root / "data" / "crop_metadata_main.json"
    if main_meta_file.exists():
        with open(main_meta_file, 'r') as f:
            main_meta = json.load(f)
            for img_name, img_data in main_meta['images'].items():
                # Extract page number from original filename (e.g., page_21_full.png -> 21)
                orig_name = img_data['original_file']
                if 'page_' in orig_name:
                    page_num = int(orig_name.split('page_')[1].split('_')[0])
                    metadata[f"main_cropped_{img_name}"] = {
                        'page': page_num,
                        'source': 'main_database',
                        'system_type': img_data['system_type'],
                        'category': 'main_db'
                    }
    
    # Load reference metadata
    ref_meta_file = project_root / "data" / "crop_metadata_reference.json"
    if ref_meta_file.exists():
        with open(ref_meta_file, 'r') as f:
            ref_meta = json.load(f)
            for img_name, img_data in ref_meta['images'].items():
                # Extract category from original filename
                orig_name = img_data['original_file']
                category = orig_name.split('_')[0] if '_' in orig_name else 'unknown'
                
                metadata[f"reference_cropped_{img_name}"] = {
                    'page': 1,  # Reference PDFs don't have page numbers in main DB
                    'source': 'reference_pdfs',
                    'system_type': img_data['system_type'],
                    'category': category,
                    'original_file': img_data['original_file']
                }
    
    return metadata

def build_image_collection(client, collection_name, embeddings, metadata):
    """
    Build ChromaDB collection for image embeddings
    
    Args:
        client: ChromaDB client
        collection_name: Name of collection
        embeddings: Dict of image embeddings
        metadata: Dict of image metadata
    """
    print(f"\n📸 Building image collection: {collection_name}")
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(name=collection_name)
        print(f"   🗑️  Deleted existing collection")
    except:
        pass
    
    # Create collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )
    
    # Prepare data for batch insertion
    ids = []
    embeddings_list = []
    metadatas = []
    documents = []
    
    for img_id, img_data in tqdm(embeddings.items(), desc="Processing images"):
        # Get metadata
        meta = metadata.get(img_id, {})
        
        # Create document text (for display purposes)
        source = meta.get('source', 'unknown')
        category = meta.get('category', 'unknown')
        system_type = meta.get('system_type', 'unknown')
        
        doc_text = f"Image: {category} ({system_type}) - Source: {source}"
        
        # Prepare metadata
        meta_dict = {
            'type': 'image',
            'source': source,
            'category': category,
            'system_type': system_type,
            'image_file': img_id,
            'page': meta.get('page', 0)
        }
        
        if 'original_file' in meta:
            meta_dict['original_file'] = meta['original_file']
        
        ids.append(img_id)
        embeddings_list.append(img_data['embedding'])
        metadatas.append(meta_dict)
        documents.append(doc_text)
    
    # Batch insert
    print(f"   💾 Inserting {len(ids)} image embeddings...")
    collection.add(
        ids=ids,
        embeddings=embeddings_list,
        metadatas=metadatas,
        documents=documents
    )
    
    print(f"   ✅ Collection '{collection_name}' created with {len(ids)} images")
    
    # Print statistics
    categories = {}
    for meta in metadatas:
        cat = meta['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n   📊 Category breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"      {cat}: {count} images")
    if len(categories) > 10:
        print(f"      ... and {len(categories) - 10} more categories")
    
    return collection

def main():
    """Main vector database building pipeline"""
    project_root = Path(__file__).parent.parent
    persist_dir = project_root / "vector_db" / "chroma_storage"
    
    print("="*70)
    print("🗄️  Building Vector Database with Image Embeddings")
    print("="*70)
    
    # Initialize ChromaDB client
    print(f"\n💾 Initializing ChromaDB at: {persist_dir}")
    client = chromadb.PersistentClient(path=str(persist_dir))
    
    # Load data
    print("\n📥 Loading data...")
    image_embeddings = load_image_embeddings()
    crop_metadata = load_crop_metadata()
    
    print(f"   ✅ Loaded {len(image_embeddings)} image embeddings")
    print(f"   ✅ Loaded metadata for {len(crop_metadata)} images")
    
    # Build image collection
    image_collection = build_image_collection(
        client,
        "hb_image_embeddings",
        image_embeddings,
        crop_metadata
    )
    
    # Summary
    print("\n" + "="*70)
    print("🎉 Vector Database Build Complete!")
    print("="*70)
    
    # Check existing text collection
    try:
        text_collection = client.get_collection("hb_patterns")
        print(f"\n📊 Collections in database:")
        print(f"   • hb_patterns (text): {text_collection.count()} vectors")
        print(f"   • hb_image_embeddings (images): {image_collection.count()} vectors")
        print(f"   Total: {text_collection.count() + image_collection.count()} vectors")
    except:
        print(f"\n📊 Collections in database:")
        print(f"   • hb_image_embeddings (images): {image_collection.count()} vectors")
        print(f"   Note: Text collection 'hb_patterns' not found (this is OK)")
    
    print(f"\n💾 Database location: {persist_dir}")
    print(f"\n💡 Next Step: Implement visual similarity search in API")
    print("="*70)

if __name__ == "__main__":
    main()

