"""
Extract text and images from PDF
Saves images to data/extracted_images/ and metadata to data/image_metadata.json
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
from PIL import Image
import io

def extract_images_from_pdf(pdf_path: str, output_dir: str, metadata_path: str):
    """
    Extract all images from PDF (including rendering vector drawings)
    
    Args:
        pdf_path: Path to input PDF
        output_dir: Directory to save extracted images
        metadata_path: Path to save image metadata JSON
    """
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Open PDF
    print(f"📖 Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    # Metadata storage
    metadata = {}
    total_images = 0
    
    # Iterate through pages
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_number = page_num + 1  # 1-indexed for humans
        
        print(f"🔍 Processing page {page_number}/{len(doc)}...", end='\r')
        
        # Method 1: Try extracting embedded raster images
        image_list = page.get_images(full=True)
        
        # Method 2: Check for vector drawings (chromatographs might be vector graphics)
        drawings = page.get_drawings()
        
        # If page has drawings but no raster images, render the page
        if drawings and not image_list:
            try:
                # Render page at high resolution (2x zoom = 144 DPI)
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL Image
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                
                # Generate filename
                filename = f"page_{page_number}_full.png"
                output_path = output_dir / filename
                
                # Save
                img.save(output_path, "PNG")
                
                # Store metadata
                metadata[filename] = {
                    "page": page_number,
                    "index": 0,
                    "width": pix.width,
                    "height": pix.height,
                    "type": "rendered_page",
                    "num_drawings": len(drawings)
                }
                
                total_images += 1
                print(f"✅ Rendered page {page_number} ({pix.width}x{pix.height}px, {len(drawings)} drawings)")
                
            except Exception as e:
                print(f"⚠️  Error rendering page {page_number}: {e}")
                continue
        
        # Extract embedded raster images (if any)
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]  # Image reference number
            
            try:
                # Get image data
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Filter out very small images (likely icons or decorations)
                img = Image.open(io.BytesIO(image_bytes))
                width, height = img.size
                
                if width < 200 or height < 200:
                    continue
                
                # Generate filename
                filename = f"page_{page_number}_img_{img_index}.png"
                output_path = output_dir / filename
                
                # Convert to PNG and save
                img.save(output_path, "PNG")
                
                # Store metadata
                metadata[filename] = {
                    "page": page_number,
                    "index": img_index,
                    "width": width,
                    "height": height,
                    "type": "embedded_image",
                    "original_format": image_ext
                }
                
                total_images += 1
                print(f"✅ Extracted embedded image from page {page_number} ({width}x{height}px)")
                
            except Exception as e:
                print(f"⚠️  Error extracting image {img_index} from page {page_number}: {e}")
                continue
    
    # Close PDF
    doc.close()
    
    # Save metadata
    metadata_path = Path(metadata_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ Extraction complete!")
    print(f"📊 Total images extracted: {total_images}")
    print(f"💾 Images saved to: {output_dir}")
    print(f"📝 Metadata saved to: {metadata_path}")
    print(f"{'='*70}")
    
    return total_images, metadata


def extract_text_from_pdf(pdf_path: str, output_path: str):
    """
    Extract text content from PDF
    
    Args:
        pdf_path: Path to input PDF
        output_path: Path to save text JSON
    """
    print(f"\n📖 Extracting text from PDF...")
    doc = fitz.open(pdf_path)
    
    text_data = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_number = page_num + 1
        
        text = page.get_text()
        text_data[f"page_{page_number}"] = {
            "page": page_number,
            "text": text.strip()
        }
    
    doc.close()
    
    # Save text data
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(text_data, f, indent=2)
    
    print(f"✅ Text extracted and saved to: {output_path}")
    
    return text_data


def main():
    """Main extraction pipeline"""
    # Paths
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "data" / "Abnormal Hb Pattern(pdf).pdf"
    output_dir = project_root / "data" / "extracted_images"
    metadata_path = project_root / "data" / "image_metadata.json"
    text_output_path = project_root / "data" / "pdf_text.json"
    
    print("="*70)
    print("🔬 Hemoglobin Pattern PDF Extraction")
    print("="*70)
    
    # Check if PDF exists
    if not pdf_path.exists():
        print(f"❌ Error: PDF not found at {pdf_path}")
        print("Please ensure the PDF is in the data/ directory")
        return
    
    # Extract images
    total_images, metadata = extract_images_from_pdf(
        str(pdf_path),
        str(output_dir),
        str(metadata_path)
    )
    
    # Extract text
    text_data = extract_text_from_pdf(str(pdf_path), str(text_output_path))
    
    print(f"\n🎉 All done! Extracted:")
    print(f"   📸 {total_images} chromatograph images")
    print(f"   📄 {len(text_data)} pages of text")
    print(f"\n💡 Next step: Run 3_build_vectordb.py to index this data")


if __name__ == "__main__":
    main()

