"""
Inspect PDF to understand image structure
"""

import fitz  # PyMuPDF
from pathlib import Path

def inspect_pdf(pdf_path: str):
    """Inspect PDF structure to find images"""
    print("="*70)
    print("🔍 PDF Inspection Tool")
    print("="*70)
    
    doc = fitz.open(pdf_path)
    
    print(f"📄 Total pages: {len(doc)}")
    
    # Check first few pages for images
    for page_num in range(min(5, len(doc))):
        page = doc[page_num]
        page_number = page_num + 1
        
        print(f"\n{'='*70}")
        print(f"📄 Page {page_number}")
        print(f"{'='*70}")
        
        # Get all images
        image_list = page.get_images(full=True)
        print(f"🖼️  Total images found: {len(image_list)}")
        
        if image_list:
            for idx, img_info in enumerate(image_list):
                xref = img_info[0]
                
                try:
                    base_image = doc.extract_image(xref)
                    width = base_image["width"]
                    height = base_image["height"]
                    ext = base_image["ext"]
                    size = len(base_image["image"])
                    
                    print(f"  Image {idx}: {width}x{height}px, format={ext}, size={size} bytes")
                    
                except Exception as e:
                    print(f"  Image {idx}: Error - {e}")
        
        # Check for drawings (vector graphics)
        drawings = page.get_drawings()
        if drawings:
            print(f"✏️  Vector drawings found: {len(drawings)}")
        
        # Check text length
        text = page.get_text()
        print(f"📝 Text length: {len(text)} characters")
        
        # Show first 200 chars of text
        if text:
            print(f"\n📖 Text preview:")
            print(text[:200].replace('\n', ' ')[:200] + "...")
    
    doc.close()


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "data" / "Abnormal Hb Pattern(pdf).pdf"
    
    if pdf_path.exists():
        inspect_pdf(str(pdf_path))
    else:
        print(f"❌ PDF not found: {pdf_path}")

