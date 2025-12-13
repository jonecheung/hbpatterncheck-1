"""
Test PDF extraction functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, get_project_root


def test_pdf_exists():
    """Test if PDF file exists"""
    config = load_config()
    project_root = get_project_root()
    pdf_path = project_root / config['pdf']['source']
    
    assert pdf_path.exists(), f"PDF not found at {pdf_path}"
    print(f"✅ PDF exists: {pdf_path}")


def test_extracted_text_exists():
    """Test if extracted text file exists"""
    config = load_config()
    project_root = get_project_root()
    text_path = project_root / config['pdf']['output_text']
    
    if text_path.exists():
        print(f"✅ Text extraction completed: {text_path}")
        return True
    else:
        print(f"⚠️  Text not yet extracted. Run: python src/1_extract_pdf.py")
        return False


def test_extracted_images_exist():
    """Test if images were extracted"""
    config = load_config()
    project_root = get_project_root()
    images_dir = project_root / config['pdf']['output_images']
    
    if images_dir.exists():
        image_count = len(list(images_dir.glob("*.png"))) + len(list(images_dir.glob("*.jpg")))
        if image_count > 0:
            print(f"✅ Images extracted: {image_count} images in {images_dir}")
            return True
        else:
            print(f"⚠️  No images found in {images_dir}")
            return False
    else:
        print(f"⚠️  Images directory doesn't exist. Run: python src/1_extract_pdf.py")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing PDF Extraction")
    print("=" * 60)
    
    test_pdf_exists()
    test_extracted_text_exists()
    test_extracted_images_exist()
    
    print("\n✅ Extraction tests complete!")

