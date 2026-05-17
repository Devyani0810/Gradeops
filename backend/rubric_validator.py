import json

def load_rubric(filepath: str) -> dict:
    with open(filepath, "r") as f:
        rubric = json.load(f)

    assert "questions" in rubric, "Rubric must have a 'questions' key"
    
    for q_id, q_data in rubric["questions"].items():
        assert "max_marks" in q_data, f"{q_id} missing 'max_marks'"
        assert "criteria" in q_data, f"{q_id} missing 'criteria'"
        
        total = sum(c["marks"] for c in q_data["criteria"])
        assert total == q_data["max_marks"], (
            f"{q_id}: criteria marks ({total}) don't add up to max_marks ({q_data['max_marks']})"
        )
    
    print("✅ Rubric is valid!")
    return rubric


if __name__ == "__main__":
    rubric = load_rubric("samples/sample_rubric.json")
    print(f"Loaded exam: {rubric['exam_title']}")
    print(f"Total marks: {rubric['total_marks']}")
    print(f"Number of questions: {len(rubric['questions'])}")