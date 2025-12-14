"""
Smart Chromatograph Cropping with Auto-Detection
Detects system type (Bio-Rad CDM or Sebia) and applies appropriate crop
"""

from PIL import Image
import pytesseract
from pathlib import Path
import json
from tqdm import tqdm

def detect_system_type(image_path):
    """
    Detect chromatograph system type by reading text in the image header
    
    Returns:
        'biorad' if Bio-Rad CDM System detected
        'sebia' if Sebia/CAPILLARYS System detected
        'unknown' if neither detected
    """
    try:
        img = Image.open(image_path)
        
        # Extract top 250 pixels (header region) for text detection
        header_region = img.crop((0, 0, img.width, 250))
        
        # Use OCR to extract text
        text = pytesseract.image_to_string(header_region).upper()
        
        # Detect Bio-Rad CDM System
        if 'BIO-RAD' in text or 'BIORAD' in text or 'CDM' in text:
            return 'biorad'
        
        # Detect Sebia System
        if 'SEBIA' in text or 'CAPILLARYS' in text or 'CAPILLARY' in text:
            return 'sebia'
        
        return 'unknown'
        
    except Exception as e:
        print(f"  ⚠️ OCR error: {e}")
        return 'unknown'

def crop_chromatograph(image_path, system_type):
    """
    Crop chromatograph based on detected system type
    
    Args:
        image_path: Path to image
        system_type: 'biorad', 'sebia', or 'unknown'
    
    Returns:
        Cropped PIL Image
    """
    img = Image.open(image_path)
    width, height = img.size
    
    if system_type == 'biorad':
        # Bio-Rad CDM System: Bottom 60%
        y_start = int(height * 0.4)
        cropped = img.crop((0, y_start, width, height))
        
    elif system_type == 'sebia':
        # Sebia System: Middle 70%
        y_start = int(height * 0.15)  # Skip top 15%
        y_end = int(height * 0.85)    # Skip bottom 15%
        cropped = img.crop((0, y_start, width, y_end))
        
    else:
        # Unknown: Use bottom 60% as fallback
        y_start = int(height * 0.4)
        cropped = img.crop((0, y_start, width, height))
    
    return cropped, system_type

def process_all_images(source_dir, output_dir, metadata_output):
    """
    Process all images with smart cropping
    
    Args:
        source_dir: Directory containing original images
        output_dir: Directory to save cropped images
        metadata_output: Path to save metadata JSON
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all images
    image_files = list(source_dir.glob("*.png"))
    
    print(f"📸 Found {len(image_files)} images to process")
    print()
    
    # Process with progress bar
    metadata = {
        'images': {},
        'stats': {
            'biorad': 0,
            'sebia': 0,
            'unknown': 0,
            'total': len(image_files)
        }
    }
    
    for img_path in tqdm(image_files, desc="Processing images"):
        try:
            # Detect system type
            system_type = detect_system_type(str(img_path))
            
            # Crop image
            cropped_img, detected_type = crop_chromatograph(str(img_path), system_type)
            
            # Save cropped image
            output_filename = f"cropped_{img_path.name}"
            output_path = output_dir / output_filename
            cropped_img.save(output_path)
            
            # Store metadata
            metadata['images'][output_filename] = {
                'original_file': img_path.name,
                'system_type': detected_type,
                'original_size': f"{cropped_img.size[0]}x{cropped_img.size[1]}",
                'crop_strategy': 'bottom_60pct' if detected_type == 'biorad' else 'middle_70pct' if detected_type == 'sebia' else 'bottom_60pct_fallback'
            }
            
            # Update stats
            metadata['stats'][detected_type] += 1
            
        except Exception as e:
            print(f"\n⚠️ Error processing {img_path.name}: {e}")
            continue
    
    # Save metadata
    metadata_path = Path(metadata_output)
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata

def main():
    """Main processing pipeline"""
    project_root = Path(__file__).parent.parent
    
    # Process both main database and reference images
    tasks = [
        {
            'name': 'Main Database',
            'source': project_root / 'data' / 'extracted_images',
            'output': project_root / 'data' / 'cropped_images_main',
            'metadata': project_root / 'data' / 'crop_metadata_main.json'
        },
        {
            'name': 'Reference PDFs',
            'source': project_root / 'data' / 'reference_images',
            'output': project_root / 'data' / 'cropped_images_reference',
            'metadata': project_root / 'data' / 'crop_metadata_reference.json'
        }
    ]
    
    print("="*70)
    print("🤖 Smart Chromatograph Cropping System")
    print("="*70)
    print()
    print("📋 Detection Rules:")
    print("   • Bio-Rad CDM System → Crop bottom 60%")
    print("   • Sebia System       → Crop middle 70%")
    print("   • Unknown            → Crop bottom 60% (fallback)")
    print()
    print("="*70)
    
    all_stats = {}
    
    for task in tasks:
        if not task['source'].exists():
            print(f"\n⚠️ Skipping {task['name']}: Source directory not found")
            continue
        
        print(f"\n📁 Processing: {task['name']}")
        print(f"   Source: {task['source']}")
        print(f"   Output: {task['output']}")
        print()
        
        metadata = process_all_images(
            str(task['source']),
            str(task['output']),
            str(task['metadata'])
        )
        
        all_stats[task['name']] = metadata['stats']
        
        print(f"\n✅ {task['name']} Complete!")
        print(f"   Bio-Rad CDM: {metadata['stats']['biorad']} images")
        print(f"   Sebia:       {metadata['stats']['sebia']} images")
        print(f"   Unknown:     {metadata['stats']['unknown']} images")
        print(f"   Total:       {metadata['stats']['total']} images")
    
    print(f"\n{'='*70}")
    print(f"🎉 All images processed!")
    print()
    print(f"📊 Overall Statistics:")
    for name, stats in all_stats.items():
        print(f"\n{name}:")
        print(f"  Bio-Rad: {stats['biorad']}")
        print(f"  Sebia:   {stats['sebia']}")
        print(f"  Unknown: {stats['unknown']}")
        print(f"  Total:   {stats['total']}")
    
    print(f"\n{'='*70}")
    print(f"💡 Next Step: Generate CLIP embeddings for cropped images")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()

