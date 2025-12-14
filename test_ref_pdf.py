import fitz
from pathlib import Path
from PIL import Image
import io

# Open a reference PDF
ref_pdf = "/Users/jc/Desktop/hbpatterncheck/hbpatterncheck/data/reference_chromatographs/hb_e/2022 08 18-22A7319104-1k1619614-homo HbE.pdf"

print(f"Opening: {ref_pdf}")
doc = fitz.open(ref_pdf)

print(f"Total pages: {len(doc)}")

for page_num in range(min(2, len(doc))):
    page = doc[page_num]
    print(f"\n Page {page_num + 1}:")
    print(f"  - Images: {len(page.get_images())}")
    print(f"  - Drawings: {len(page.get_drawings())}")
    
    # Render page
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    output_path = f"/Users/jc/Desktop/hbpatterncheck/hbpatterncheck/test_ref_page_{page_num + 1}.png"
    pix.save(output_path)
    print(f"  - Rendered to: {output_path}")

doc.close()
print("\nDone! Opening rendered page...")

import subprocess
subprocess.run(["open", "/Users/jc/Desktop/hbpatterncheck/hbpatterncheck/test_ref_page_1.png"])

