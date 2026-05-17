import json
import re

def load_rubric(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return json.load(f)


def map_text_to_questions(extracted_pages: dict, rubric: dict) -> dict:
    """
    Takes extracted text from all pages and maps it to question numbers.
    Returns a dict like:
    {
        "question_1": "student's answer text...",
        "question_2": "student's answer text...",
    }
    """
    
    mapped_answers = {}
    
    # Combine all page texts into one big string
    full_text = "\n".join(extracted_pages.values())
    
    print("🔍 Attempting to map answers to questions...\n")
    
    # Get question IDs from rubric
    question_ids = list(rubric["questions"].keys())
    
    for i, question_id in enumerate(question_ids):
        # Try to find text between this question number and the next
        # This is a simple approach - looks for "Q1", "Q.1", "1.", "Question 1"
        
        current_num = i + 1
        next_num = i + 2
        
        # Pattern to find question markers
        patterns = [
            rf"[Qq]\.?\s*{current_num}[.):\s]",  # Q1, Q.1, Q1:
            rf"[Qq]uestion\s*{current_num}[.):\s]",  # Question 1
            rf"^\s*{current_num}[.):\s]",  # 1. or 1)
        ]
        
        start_pos = None
        for pattern in patterns:
            match = re.search(pattern, full_text, re.MULTILINE)
            if match:
                start_pos = match.end()
                break
        
        if start_pos is None:
            print(f"⚠️  Could not find marker for {question_id}")
            mapped_answers[question_id] = "ANSWER NOT FOUND"
            continue
        
        # Find where next question starts
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
        
        # Extract the answer
        answer_text = full_text[start_pos:end_pos].strip()
        mapped_answers[question_id] = answer_text
        
        print(f"✅ {question_id}: found ({len(answer_text)} characters)")
    
    return mapped_answers


def save_mapped_answers(mapped_answers: dict, output_path: str):
    """Save mapped answers to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(mapped_answers, f, indent=2)
    print(f"\n💾 Saved mapped answers to {output_path}")


# Test it
if __name__ == "__main__":
    from ocr_engine import extract_text_from_all_pages
    
    # Step 1: Get OCR results
    image_folder = "samples/extracted_images"
    extracted_pages = extract_text_from_all_pages(image_folder)
    
    # Step 2: Load rubric
    rubric = load_rubric("samples/sample_rubric.json")
    
    # Step 3: Map to questions
    mapped_answers = map_text_to_questions(extracted_pages, rubric)
    
    # Step 4: Save results
    save_mapped_answers(mapped_answers, "samples/mapped_answers.json")
    
    # Step 5: Print summary
    print("\n" + "="*50)
    print("MAPPED ANSWERS SUMMARY")
    print("="*50)
    for q_id, answer in mapped_answers.items():
        print(f"\n{q_id.upper()}:")
        print(answer[:200] + "..." if len(answer) > 200 else answer)