"""
Extract all pages from reference chromatograph PDFs
Maintains multi-page structure for each PDF file
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
from PIL import Image
import io

def extract_reference_pdfs(reference_dir: str, output_dir: str, metadata_path: str):
    """
    Extract all pages from reference PDFs, maintaining multi-page structure
    
    Args:
        reference_dir: Root directory containing reference PDF folders
        output_dir: Directory to save extracted images
        metadata_path: Path to save metadata JSON
    """
    reference_dir = Path(reference_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "pdfs": {},  # PDF-level metadata
        "images": {}  # Individual image metadata
    }
    
    total_pdfs = 0
    total_pages = 0
    
    # Get all PDF files recursively
    pdf_files = list(reference_dir.rglob("*.pdf"))
    
    print("="*70)
    print(f"🔬 Extracting Reference Chromatographs")
    print("="*70)
    print(f"📂 Found {len(pdf_files)} PDF files")
    print()
    
    for pdf_path in pdf_files:
        # Get category from parent folder
        category = pdf_path.parent.name
        
        # Generate a safe base filename
        pdf_basename = pdf_path.stem  # filename without extension
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in pdf_basename)
        
        try:
            doc = fitz.open(str(pdf_path))
            num_pages = len(doc)
            
            print(f"📄 Processing: {pdf_path.name}")
            print(f"   Category: {category}, Pages: {num_pages}")
            
            # Store PDF metadata
            pdf_key = f"{category}_{safe_name}"
            metadata["pdfs"][pdf_key] = {
                "original_filename": pdf_path.name,
                "category": category,
                "num_pages": num_pages,
                "pages": []
            }
            
            # Extract each page
            for page_num in range(num_pages):
                page = doc[page_num]
                
                # Generate filename: category_pdfname_pageN.png
                image_filename = f"{pdf_key}_page{page_num + 1}.png"
                output_path = output_dir / image_filename
                
                # Render page at high resolution
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Save
                pix.save(str(output_path))
                
                # Store image metadata
                metadata["images"][image_filename] = {
                    "pdf_key": pdf_key,
                    "category": category,
                    "original_pdf": pdf_path.name,
                    "page_number": page_num + 1,
                    "width": pix.width,
                    "height": pix.height
                }
                
                # Add to PDF's page list
                metadata["pdfs"][pdf_key]["pages"].append(image_filename)
                
                total_pages += 1
                print(f"      ✅ Page {page_num + 1}: {image_filename} ({pix.width}x{pix.height}px)")
            
            doc.close()
            total_pdfs += 1
            print()
            
        except Exception as e:
            print(f"      ⚠️ Error processing {pdf_path.name}: {e}")
            print()
            continue
    
    # Save metadata
    metadata_path = Path(metadata_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("="*70)
    print(f"✅ Extraction complete!")
    print(f"📊 Processed {total_pdfs} PDFs")
    print(f"📸 Extracted {total_pages} pages")
    print(f"💾 Images saved to: {output_dir}")
    print(f"📝 Metadata saved to: {metadata_path}")
    print("="*70)
    
    # Print summary by category
    print("\n📊 Summary by Category:")
    category_counts = {}
    for pdf_data in metadata["pdfs"].values():
        cat = pdf_data["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items()):
        print(f"   {cat}: {count} PDFs")
    
    return metadata


def main():
    """Main extraction pipeline for reference PDFs"""
    project_root = Path(__file__).parent.parent
    reference_dir = project_root / "data" / "reference_chromatographs"
    output_dir = project_root / "data" / "reference_images"
    metadata_path = project_root / "data" / "reference_metadata.json"
    
    if not reference_dir.exists():
        print(f"❌ Error: Reference directory not found at {reference_dir}")
        return
    
    metadata = extract_reference_pdfs(
        str(reference_dir),
        str(output_dir),
        str(metadata_path)
    )
    
    print(f"\n💡 Next step: Run 3_build_vectordb.py to index these images")


if __name__ == "__main__":
    main()

