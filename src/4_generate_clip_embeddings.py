con"""
Generate CLIP embeddings for all cropped chromatograph images
"""

import open_clip
import torch
from PIL import Image
from pathlib import Path
import json
import numpy as np
from tqdm import tqdm

def generate_clip_embeddings(image_dir, output_file, model, preprocess, device='cpu'):
    """
    Generate CLIP embeddings for all images in a directory
    
    Args:
        image_dir: Directory containing images
        output_file: Path to save embeddings JSON
        model: CLIP model
        preprocess: CLIP preprocessing function
        device: 'cpu' or 'cuda' or 'mps'
    
    Returns:
        Dictionary of embeddings
    """
    image_dir = Path(image_dir)
    image_files = list(image_dir.glob("*.png"))
    
    if not image_files:
        print(f"⚠️  No images found in {image_dir}")
        return {}
    
    print(f"📸 Processing {len(image_files)} images from {image_dir.name}")
    
    embeddings_data = {}
    
    # Process images with progress bar
    for img_path in tqdm(image_files, desc=f"Embedding {image_dir.name}"):
        try:
            # Load and preprocess image
            image = Image.open(img_path).convert('RGB')
            image_input = preprocess(image).unsqueeze(0).to(device)
            
            # Generate embedding
            with torch.no_grad():
                embedding = model.encode_image(image_input)
                # Normalize embedding
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                # Convert to numpy and then to list for JSON serialization
                embedding_list = embedding.cpu().numpy()[0].tolist()
            
            # Store embedding with metadata
            embeddings_data[img_path.name] = {
                'embedding': embedding_list,
                'embedding_dim': len(embedding_list),
                'original_file': img_path.name,
                'image_size': f"{image.size[0]}x{image.size[1]}"
            }
            
        except Exception as e:
            print(f"\n⚠️ Error processing {img_path.name}: {e}")
            continue
    
    # Save embeddings
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(embeddings_data, f, indent=2)
    
    print(f"✅ Saved {len(embeddings_data)} embeddings to {output_path}")
    
    return embeddings_data

def main():
    """Main embedding generation pipeline"""
    project_root = Path(__file__).parent.parent
    
    print("="*70)
    print("🎨 CLIP Embedding Generation")
    print("="*70)
    
    # Check for Apple Silicon GPU
    if torch.backends.mps.is_available():
        device = 'mps'
        print("✅ Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = 'cuda'
        print("✅ Using NVIDIA GPU (CUDA)")
    else:
        device = 'cpu'
        print("ℹ️  Using CPU (slower but works)")
    
    print()
    print("🔄 Loading CLIP model...")
    
    # Load CLIP model
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-32', 
        pretrained='openai'
    )
    model.eval()
    model.to(device)
    
    print("✅ CLIP model loaded")
    print(f"   Model: ViT-B-32")
    print(f"   Embedding dimension: 512")
    print(f"   Device: {device}")
    print()
    
    # Process both main database and reference images
    tasks = [
        {
            'name': 'Main Database',
            'input_dir': project_root / 'data' / 'cropped_images_main',
            'output_file': project_root / 'data' / 'clip_embeddings_main.json'
        },
        {
            'name': 'Reference PDFs',
            'input_dir': project_root / 'data' / 'cropped_images_reference',
            'output_file': project_root / 'data' / 'clip_embeddings_reference.json'
        }
    ]
    
    all_embeddings = {}
    total_processed = 0
    
    for task in tasks:
        if not task['input_dir'].exists():
            print(f"⚠️  Skipping {task['name']}: Directory not found")
            continue
        
        print(f"{'='*70}")
        print(f"📁 {task['name']}")
        print(f"{'='*70}")
        
        embeddings = generate_clip_embeddings(
            str(task['input_dir']),
            str(task['output_file']),
            model,
            preprocess,
            device
        )
        
        all_embeddings[task['name']] = embeddings
        total_processed += len(embeddings)
        print()
    
    # Summary
    print("="*70)
    print("🎉 Embedding Generation Complete!")
    print("="*70)
    print()
    print("📊 Summary:")
    for name, embeddings in all_embeddings.items():
        print(f"   {name}: {len(embeddings)} images")
    print(f"   Total: {total_processed} images")
    print()
    
    # File sizes
    print("💾 Output Files:")
    for task in tasks:
        if task['output_file'].exists():
            size_mb = task['output_file'].stat().st_size / (1024 * 1024)
            print(f"   {task['output_file'].name}: {size_mb:.1f} MB")
    print()
    
    print("="*70)
    print("💡 Next Step: Rebuild vector database with image embeddings")
    print("="*70)

if __name__ == "__main__":
    main()

