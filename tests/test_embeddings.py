"""
Test embedding generation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sentence_transformers import SentenceTransformer
from utils import load_config


def test_embedding_model():
    """Test if embedding model can be loaded"""
    config = load_config()
    model_name = config['embeddings']['model']
    
    print(f"📥 Loading embedding model: {model_name}")
    try:
        model = SentenceTransformer(model_name)
        print(f"✅ Model loaded successfully")
        
        # Test encoding
        test_text = "This is a test sentence for hemoglobin pattern analysis."
        embedding = model.encode(test_text)
        
        print(f"✅ Test encoding successful")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   Expected dimension: {config['embeddings']['dimension']}")
        
        assert len(embedding) == config['embeddings']['dimension'], "Dimension mismatch!"
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Embedding Model")
    print("=" * 60)
    
    test_embedding_model()
    
    print("\n✅ Embedding tests complete!")

