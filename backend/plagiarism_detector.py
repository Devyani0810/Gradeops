from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os


def detect_plagiarism(
    student_answers: dict,
    question_id: str,
    threshold: float = 0.85
) -> list:
    """
    Checks all student answers for a question and flags
    suspicious pairs above the similarity threshold.
    
    student_answers format:
    {
        "student_001": "answer text...",
        "student_002": "answer text...",
    }
    
    Returns list of flagged pairs with similarity scores.
    """
    
    print(f"\n🔍 Checking plagiarism for {question_id}...")
    print(f"   Comparing {len(student_answers)} student answers")
    print(f"   Threshold: {threshold * 100}% similarity\n")
    
    # Need at least 2 students to compare
    if len(student_answers) < 2:
        print("  ⚠️  Need at least 2 students to compare")
        return []
    
    # Get student IDs and their answers
    student_ids = list(student_answers.keys())
    answers = list(student_answers.values())
    
    # Convert answers to TF-IDF vectors
    # TF-IDF = Term Frequency-Inverse Document Frequency
    # It measures how important a word is in a document
    vectorizer = TfidfVectorizer(
        stop_words="english",  # ignore common words like "the", "is"
        min_df=1
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(answers)
    except Exception as e:
        print(f"  ❌ Error creating vectors: {e}")
        return []
    
    # Calculate similarity between all pairs
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    flagged_pairs = []
    
    # Compare every student with every other student
    for i in range(len(student_ids)):
        for j in range(i + 1, len(student_ids)):
            similarity = similarity_matrix[i][j]
            
            if similarity >= threshold:
                pair = {
                    "question_id": question_id,
                    "student_1": student_ids[i],
                    "student_2": student_ids[j],
                    "similarity_score": round(float(similarity), 4),
                    "similarity_percent": f"{round(similarity * 100, 1)}%",
                    "status": "FLAGGED_FOR_REVIEW"
                }
                flagged_pairs.append(pair)
                print(f"  🚨 FLAGGED: {student_ids[i]} & {student_ids[j]}")
                print(f"     Similarity: {pair['similarity_percent']}")
            else:
                print(f"  ✅ {student_ids[i]} & {student_ids[j]}: {round(similarity*100,1)}% (OK)")
    
    return flagged_pairs


def run_plagiarism_check_for_exam(all_student_answers: dict, threshold: float = 0.85) -> dict:
    """
    Runs plagiarism check for all questions in an exam.
    
    all_student_answers format:
    {
        "question_1": {
            "student_001": "answer...",
            "student_002": "answer...",
        },
        "question_2": { ... }
    }
    """
    
    all_flags = {}
    
    for question_id, student_answers in all_student_answers.items():
        flags = detect_plagiarism(student_answers, question_id, threshold)
        if flags:
            all_flags[question_id] = flags
    
    return all_flags


def save_plagiarism_report(flags: dict, output_path: str):
    """Save plagiarism report to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(flags, f, indent=2)
    print(f"\n💾 Plagiarism report saved to {output_path}")


# Test it
if __name__ == "__main__":
    
    # Simulating 4 students answering the same question
    # Students 1 and 2 have very similar answers (suspicious!)
    # Students 3 and 4 have original answers
    
    test_answers = {
        "question_1": {
            "student_001": """
                The OSI model has seven layers physical data link network 
                transport session presentation application. Each layer has 
                specific functions for network communication protocol.
            """,
            "student_002": """
                The OSI model has seven layers physical data link network 
                transport session presentation application. Each layer has 
                specific functions for network communication protocol.
            """,  # Almost identical to student_001!
            "student_003": """
                OSI stands for Open Systems Interconnection. It was developed 
                by ISO to standardize networking. The seven layers work together 
                to enable devices from different manufacturers to communicate.
            """,
            "student_004": """
                The OSI reference model defines how data travels across a network.
                Starting from the bottom, physical layer handles cables and signals.
                Network layer routes packets using IP addresses between systems.
            """
        }
    }
    
    print("🚀 Running Plagiarism Detection")
    print("="*50)
    
    # Run the check
    flags = run_plagiarism_check_for_exam(test_answers, threshold=0.85)
    
    # Save report
    save_plagiarism_report(flags, "samples/plagiarism_report.json")
    
    # Print summary
    print("\n" + "="*50)
    print("PLAGIARISM DETECTION SUMMARY")
    print("="*50)
    
    if not flags:
        print("✅ No plagiarism detected!")
    else:
        total_flags = sum(len(v) for v in flags.values())
        print(f"🚨 {total_flags} suspicious pair(s) found!\n")
        for q_id, pairs in flags.items():
            print(f"{q_id}:")
            for pair in pairs:
                print(f"  {pair['student_1']} ↔ {pair['student_2']}: {pair['similarity_percent']}")