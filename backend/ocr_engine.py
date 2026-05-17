import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path: str) -> str:
    """
    Takes an image path and returns the extracted text using OCR.
    """
    
    # Open the image
    image = Image.open(image_path)
    
    # Run OCR
    extracted_text = pytesseract.image_to_string(image)
    
    return extracted_text.strip()


def extract_text_from_all_pages(image_folder: str) -> dict:
    """
    Runs OCR on all page images in a folder.
    Returns a dict like: {"page_1": "extracted text...", "page_2": "..."}
    """
    
    results = {}
    
    # Get all PNG files sorted by page number
    image_files = sorted([
        f for f in os.listdir(image_folder) 
        if f.endswith(".png")
    ])
    
    if not image_files:
        print("❌ No images found in folder!")
        return results
    
    print(f"🔍 Running OCR on {len(image_files)} page(s)...\n")
    
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        page_name = image_file.replace(".png", "")
        
        print(f"Processing {image_file}...")
        text = extract_text_from_image(image_path)
        results[page_name] = text
        
        print(f"✅ {page_name} extracted ({len(text)} characters)\n")
    
    return results


# Test it
if __name__ == "__main__":
    image_folder = "samples/extracted_images"
    
    # Run OCR on all pages
    results = extract_text_from_all_pages(image_folder)
    
    # Print results
    print("\n" + "="*50)
    print("EXTRACTED TEXT RESULTS")
    print("="*50)
    
    for page, text in results.items():
        print(f"\n📄 {page.upper()}:")
        print("-" * 30)
        print(text if text else "(no text detected)")
        print("-" * 30)