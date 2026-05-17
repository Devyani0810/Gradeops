import fitz  # this is PyMuPDF
import os

def pdf_to_images(pdf_path: str, output_folder: str) -> list:
    """
    Takes a PDF file and converts each page into a PNG image.
    Returns a list of image file paths.
    """
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    image_paths = []
    
    print(f"📄 PDF has {len(pdf_document)} page(s)")
    
    # Loop through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        
        # Convert page to image
        # zoom=2 makes it higher resolution (better for OCR)
        zoom = 2
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        
        # Save the image
        image_filename = f"page_{page_number + 1}.png"
        image_path = os.path.join(output_folder, image_filename)
        pixmap.save(image_path)
        
        image_paths.append(image_path)
        print(f"✅ Saved page {page_number + 1} as {image_filename}")
    
    pdf_document.close()
    
    print(f"\n🎉 All pages extracted to: {output_folder}")
    return image_paths


# Test it
if __name__ == "__main__":
    # Input PDF path
    pdf_path = "samples/pdfs/test_exam.pdf"
    
    # Where to save the images
    output_folder = "samples/extracted_images"
    
    # Run the extractor
    image_paths = pdf_to_images(pdf_path, output_folder)
    
    print(f"\nExtracted {len(image_paths)} image(s):")
    for path in image_paths:
        print(f"  - {path}")