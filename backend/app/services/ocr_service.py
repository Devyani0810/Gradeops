"""
app/services/ocr_service.py
Standardized: Supports BOTH PDF and Photo Uploads with Native Python Logging
"""
import os
import re
from pathlib import Path
import fitz  # Modern PyMuPDF
from PIL import Image
import io
import pytesseract
from app.config import settings

# Update this path to where Tesseract is installed on your Windows machine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRService:
    async def extract(
        self, file_bytes: bytes, rubric: dict, submission_id: str, filename: str = ""
    ) -> tuple[dict[str, str], dict[str, str]]:
        
        print(f"📡 Starting OCR extraction for submission: {submission_id} (File: {filename})")
        full_text = ""
        image_keys: dict[str, str] = {}
        
        # Check if the uploaded file is a raw image instead of a PDF
        is_image = filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))
        
        if is_image:
            print("📸 Processing file directly as a raw image photo...")
            key = f"page_images/{submission_id}/uploaded_photo.png"
            dest = Path(settings.LOCAL_UPLOAD_DIR) / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            image = Image.open(io.BytesIO(file_bytes))
            image.save(str(dest))
            
            full_text = pytesseract.image_to_string(image)
            question_id = list(rubric.keys())[0] if rubric else "q1"
            image_keys[question_id] = key
            
        else:
            print("📄 Processing file as a standard PDF document...")
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            for page_number in range(len(doc)):
                page = doc[page_number]
                zoom = 2
                matrix = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=matrix)
                
                key = f"page_images/{submission_id}/page_{page_number + 1}.png"
                dest = Path(settings.LOCAL_UPLOAD_DIR) / key
                dest.parent.mkdir(parents=True, exist_ok=True)
                pix.save(str(dest))
                
                if page_number == 0:
                    question_id = list(rubric.keys())[0] if rubric else "q1"
                    image_keys[question_id] = key

                image = Image.open(str(dest))
                page_text = pytesseract.image_to_string(image)
                full_text += page_text + "\n"
                
            doc.close()

        # Run regex mapping block
        extracted_mapped_text = self._map_text_to_questions(full_text, rubric)
        return extracted_mapped_text, image_keys

    def _map_text_to_questions(self, full_text: str, rubric: dict) -> dict:
        mapped_answers = {}
        question_ids = list(rubric.keys())
        
        for i, question_id in enumerate(question_ids):
            current_num = i + 1
            next_num = i + 2
            
            patterns = [
                rf"[Qq]\.?\s*{current_num}[.):\s]",  
                rf"[Qq]uestion\s*{current_num}[.):\s]",  
                rf"^\s*{current_num}[.):\s]",  
            ]
            
            start_pos = None
            for pattern in patterns:
                match = re.search(pattern, full_text, re.MULTILINE)
                if match:
                    start_pos = match.end()
                    break
            
            if start_pos is None:
                print(f"⚠️ Could not find marker for {question_id}")
                mapped_answers[question_id] = "ANSWER NOT FOUND"
                continue
            
            end_pos = len(full_text)
            for next_pattern in [
                rf"[Qq]\.?\s*{next_num}[.):\s]",
                rf"[Qq]uestion\s*{next_num}[.):\s]",
                rf"^\s*{next_num}[.):\s]",
            ]:
                next_match = re.search(next_pattern, full_text[start_pos:], re.MULTILINE)
                if next_match:
                    end_pos = start_pos + next_match.start()
                    break
            
            answer_text = full_text[start_pos:end_pos].strip()
            mapped_answers[question_id] = answer_text
            
        return mapped_answers