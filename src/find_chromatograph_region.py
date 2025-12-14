"""
Interactive tool to find chromatograph regions in images
Creates sample crops for visual inspection
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_crop_samples(image_path, output_dir):
    """
    Create sample crops from different regions to help identify chromatograph location
    """
    img = Image.open(image_path)
    width, height = img.size
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define different crop strategies
    crop_strategies = {
        "full": (0, 0, width, height),  # Original
        "bottom_half": (0, height//2, width, height),  # Bottom 50%
        "bottom_third": (0, 2*height//3, width, height),  # Bottom 33%
        "middle_third": (0, height//3, width, 2*height//3),  # Middle 33%
        "bottom_60pct": (0, int(height*0.4), width, height),  # Bottom 60%
        "center_square": (width//4, height//4, 3*width//4, 3*height//4),  # Center square
    }
    
    base_name = Path(image_path).stem
    saved_crops = []
    
    for strategy_name, (x1, y1, x2, y2) in crop_strategies.items():
        # Crop image
        cropped = img.crop((x1, y1, x2, y2))
        
        # Save crop
        output_path = output_dir / f"{base_name}_{strategy_name}.png"
        cropped.save(output_path)
        saved_crops.append((strategy_name, output_path, cropped.size))
    
    return saved_crops

def main():
    """Test on sample images"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "crop_samples"
    
    # Test on a few representative images
    test_images = [
        project_root / "data" / "reference_images" / "hb_e_2022_08_18-22A7319104-1k1619614-homo_HbE_page1.png",
        project_root / "data" / "reference_images" / "hb_e_2022_08_18-22A7319104-1k1619614-homo_HbE_page2.png",
        project_root / "data" / "reference_images" / "constant_spring_2022_11_03-22A7452784-1u3770718-HbH-Constant_Spring__page1.png",
    ]
    
    print("="*70)
    print("🔍 Creating Crop Samples")
    print("="*70)
    
    for img_path in test_images:
        if not img_path.exists():
            print(f"⚠️  Skipping {img_path.name} (not found)")
            continue
        
        print(f"\n📸 Processing: {img_path.name}")
        crops = create_crop_samples(str(img_path), str(output_dir))
        
        for strategy, path, size in crops:
            print(f"   ✅ {strategy}: {size[0]}x{size[1]} → {path.name}")
    
    print(f"\n{'='*70}")
    print(f"✅ Crop samples saved to: {output_dir}")
    print(f"")
    print(f"📋 Next Steps:")
    print(f"   1. Open {output_dir}")
    print(f"   2. Find which crop strategy captures the chromatograph best")
    print(f"   3. Tell me which strategy works (e.g., 'bottom_half')")
    print(f"{'='*70}")
    
    # Open the folder
    import subprocess
    subprocess.run(["open", str(output_dir)])

if __name__ == "__main__":
    main()

