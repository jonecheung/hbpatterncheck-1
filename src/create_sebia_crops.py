"""
Create additional crop strategies for Sebia chromatograph system
"""

from PIL import Image
from pathlib import Path

def create_sebia_crops(image_path, output_dir):
    """
    Create various crop strategies specifically for Sebia system
    """
    img = Image.open(image_path)
    width, height = img.size
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extended crop strategies for Sebia
    crop_strategies = {
        # Original working crop
        "bottom_60pct": (0, int(height*0.4), width, height),
        
        # Try different vertical positions
        "top_40pct": (0, 0, width, int(height*0.4)),
        "top_50pct": (0, 0, width, int(height*0.5)),
        "top_60pct": (0, 0, width, int(height*0.6)),
        
        # Middle sections
        "middle_40pct": (0, int(height*0.3), width, int(height*0.7)),
        "middle_50pct": (0, int(height*0.25), width, int(height*0.75)),
        "middle_60pct": (0, int(height*0.2), width, int(height*0.8)),
        
        # Different bottom crops
        "bottom_40pct": (0, int(height*0.6), width, height),
        "bottom_50pct": (0, int(height*0.5), width, height),
        "bottom_70pct": (0, int(height*0.3), width, height),
        "bottom_80pct": (0, int(height*0.2), width, height),
        
        # Skip header/footer regions
        "skip_header": (0, 150, width, height),  # Skip top 150px
        "skip_both": (0, 150, width, height-100),  # Skip top 150px + bottom 100px
        
        # Full width but specific heights
        "middle_800px": (0, int(height/2-400), width, int(height/2+400)),
        "middle_1000px": (0, int(height/2-500), width, int(height/2+500)),
    }
    
    base_name = Path(image_path).stem
    saved_crops = []
    
    for strategy_name, (x1, y1, x2, y2) in crop_strategies.items():
        try:
            # Ensure coordinates are valid
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Crop image
            cropped = img.crop((x1, y1, x2, y2))
            
            # Save crop
            output_path = output_dir / f"{base_name}_SEBIA_{strategy_name}.png"
            cropped.save(output_path)
            saved_crops.append((strategy_name, output_path, cropped.size))
        except Exception as e:
            print(f"  ⚠️ Error with {strategy_name}: {e}")
    
    return saved_crops

def main():
    """Create Sebia-specific crops"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "sebia_crop_samples"
    
    # Test on the same images
    test_images = [
        project_root / "data" / "reference_images" / "hb_e_2022_08_18-22A7319104-1k1619614-homo_HbE_page1.png",
        project_root / "data" / "reference_images" / "hb_e_2022_08_18-22A7319104-1k1619614-homo_HbE_page2.png",
        project_root / "data" / "reference_images" / "constant_spring_2022_11_03-22A7452784-1u3770718-HbH-Constant_Spring__page1.png",
    ]
    
    print("="*70)
    print("🔍 Creating Sebia-Specific Crop Samples")
    print("="*70)
    
    for img_path in test_images:
        if not img_path.exists():
            print(f"⚠️  Skipping {img_path.name} (not found)")
            continue
        
        print(f"\n📸 Processing: {img_path.name}")
        crops = create_sebia_crops(str(img_path), str(output_dir))
        
        print(f"   Created {len(crops)} crop variations")
        for strategy, path, size in crops[:5]:  # Show first 5
            print(f"   ✅ {strategy}: {size[0]}x{size[1]}")
        if len(crops) > 5:
            print(f"   ... and {len(crops)-5} more")
    
    print(f"\n{'='*70}")
    print(f"✅ Sebia crop samples saved to: {output_dir}")
    print(f"")
    print(f"📋 Crop Strategies Tested:")
    print(f"   • Top sections: top_40pct, top_50pct, top_60pct")
    print(f"   • Middle sections: middle_40pct, middle_50pct, middle_60pct")
    print(f"   • Bottom sections: bottom_40/50/60/70/80pct")
    print(f"   • Skip header/footer: skip_header, skip_both")
    print(f"   • Fixed heights: middle_800px, middle_1000px")
    print(f"")
    print(f"🔍 Next Steps:")
    print(f"   1. Open the folder (opening now...)")
    print(f"   2. Find which crops show Sebia chromatographs clearly")
    print(f"   3. Tell me which strategy works!")
    print(f"{'='*70}")
    
    # Open the folder
    import subprocess
    subprocess.run(["open", str(output_dir)])

if __name__ == "__main__":
    main()

