import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

# Grading prompt template
GRADING_PROMPT = PromptTemplate(
    input_variables=["question_text", "rubric_criteria", "max_marks", "student_answer"],
    template="""
You are a strict but fair university exam grader.

QUESTION:
{question_text}

MAXIMUM MARKS: {max_marks}

GRADING RUBRIC:
{rubric_criteria}

STUDENT'S ANSWER:
{student_answer}

INSTRUCTIONS:
- Grade strictly based on the rubric criteria only
- Award partial marks where partially correct
- Be consistent and objective
- Do not award more than the maximum marks for each criterion

You MUST respond with ONLY a valid JSON object in exactly this format, nothing else:
{{
"score": <total score as a number>,
"justification": "<overall justification in 2-3 sentences>",
"criteria_breakdown": [
    {{
    "criterion": "<criterion point>",
    "marks_awarded": <marks given>,
    "max_marks": <max marks for this criterion>,
    "reason": "<why these marks were given>"
    }}
]
}}
"""
)


def format_rubric_criteria(criteria: list) -> str:
    """Format criteria list into readable text for the prompt."""
    formatted = ""
    for i, criterion in enumerate(criteria, 1):
        formatted += f"{i}. {criterion['point']} — {criterion['marks']} marks\n"
    return formatted


def grade_single_answer(
    question_text: str,
    criteria: list,
    max_marks: int,
    student_answer: str
) -> dict:
    """
    Grade a single student answer against a rubric.
    Returns a dict with score, justification, and breakdown.
    """

    rubric_criteria = format_rubric_criteria(criteria)

    # Handle empty or missing answers
    if not student_answer or student_answer == "ANSWER NOT FOUND":
        return {
            "score": 0,
            "justification": "No answer provided by student.",
            "criteria_breakdown": [
                {
                    "criterion": c["point"],
                    "marks_awarded": 0,
                    "max_marks": c["marks"],
                    "reason": "No answer provided"
                }
                for c in criteria
            ]
        }

    # Create and run the chain
    chain = GRADING_PROMPT | llm

    print(f"  🤖 Sending to Groq AI grader...")
    response = chain.invoke({
        "question_text": question_text,
        "rubric_criteria": rubric_criteria,
        "max_marks": max_marks,
        "student_answer": student_answer
    })

    # Parse response
    response_text = response.content.strip()

    # Clean up markdown code blocks if present
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    # Parse JSON
    result = json.loads(response_text)

    # Cap score at max marks
    result["score"] = min(result["score"], max_marks)

    return result


# Test it
if __name__ == "__main__":
    question_text = "Explain the OSI model and its layers."

    criteria = [
        {"point": "Named all 7 layers correctly", "marks": 3},
        {"point": "Explained function of at least 4 layers", "marks": 4},
        {"point": "Gave a real-world example", "marks": 3}
    ]

    max_marks = 10

    student_answer = """
    The OSI model has 7 layers: Physical, Data Link, Network, Transport,
    Session, Presentation, and Application layer.
    The Physical layer deals with raw bits over cables.
    The Network layer handles routing using IP addresses.
    The Transport layer ensures reliable delivery using TCP.
    The Application layer is what users interact with like HTTP for websites.
    """

    print("📝 Grading sample answer...\n")
    result = grade_single_answer(question_text, criteria, max_marks, student_answer)

    print("\n" + "="*50)
    print("GRADING RESULT")
    print("="*50)
    print(f"Score: {result['score']}/{max_marks}")
    print(f"Justification: {result['justification']}")
    print("\nBreakdown:")
    for item in result["criteria_breakdown"]:
        print(f"  - {item['criterion']}")
        print(f"    Marks: {item['marks_awarded']}/{item['max_marks']}")
        print(f"    Reason: {item['reason']}")