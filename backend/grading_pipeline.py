import json
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from grader import grade_single_answer


# Define what our pipeline state looks like
# This is like a shared notebook passed between each node
class GradingState(TypedDict):
    student_id: str
    question_id: str
    question_text: str
    criteria: list
    max_marks: int
    student_answer: str
    grading_result: dict
    is_valid: bool
    error: str


# ─────────────────────────────────────────
# NODE 1: Receive and prepare input
# ─────────────────────────────────────────
def node_receive_input(state: GradingState) -> GradingState:
    """
    Node 1: Validates that we have all required inputs
    before sending to the grader.
    """
    print(f"\n📥 Node 1: Receiving input for {state['question_id']}...")
    
    # Check all required fields exist
    required_fields = ["student_answer", "criteria", "max_marks", "question_text"]
    for field in required_fields:
        if not state.get(field):
            state["is_valid"] = False
            state["error"] = f"Missing required field: {field}"
            print(f"  ❌ Missing: {field}")
            return state
    
    state["is_valid"] = True
    print(f"  ✅ Input validated for student: {state['student_id']}")
    return state


# ─────────────────────────────────────────
# NODE 2: Call the LLM grader
# ─────────────────────────────────────────
def node_call_grader(state: GradingState) -> GradingState:
    """
    Node 2: Sends answer to AI grader and gets result.
    """
    print(f"\n🤖 Node 2: Calling AI grader...")
    
    # Skip if input was invalid
    if not state["is_valid"]:
        print("  ⏭️  Skipping — invalid input")
        return state
    
    try:
        result = grade_single_answer(
            question_text=state["question_text"],
            criteria=state["criteria"],
            max_marks=state["max_marks"],
            student_answer=state["student_answer"]
        )
        state["grading_result"] = result
        print(f"  ✅ AI graded: {result['score']}/{state['max_marks']}")
        
    except Exception as e:
        state["is_valid"] = False
        state["error"] = f"Grading failed: {str(e)}"
        print(f"  ❌ Error: {e}")
    
    return state


# ─────────────────────────────────────────
# NODE 3: Validate the result
# ─────────────────────────────────────────
def node_validate_result(state: GradingState) -> GradingState:
    """
    Node 3: Makes sure the AI result is valid.
    - Score doesn't exceed max marks
    - All required fields present
    """
    print(f"\n✅ Node 3: Validating result...")
    
    if not state["is_valid"]:
        print("  ⏭️  Skipping — previous error")
        return state
    
    result = state["grading_result"]
    
    # Check score is within bounds
    if result["score"] > state["max_marks"]:
        print(f"  ⚠️  Score {result['score']} exceeded max {state['max_marks']}, capping it")
        result["score"] = state["max_marks"]
    
    if result["score"] < 0:
        print(f"  ⚠️  Negative score found, setting to 0")
        result["score"] = 0
    
    # Check required fields exist
    if "justification" not in result:
        result["justification"] = "No justification provided"
    
    if "criteria_breakdown" not in result:
        result["criteria_breakdown"] = []
    
    state["grading_result"] = result
    state["is_valid"] = True
    print(f"  ✅ Result is valid")
    return state


# ─────────────────────────────────────────
# NODE 4: Store the result
# ─────────────────────────────────────────
def node_store_result(state: GradingState) -> GradingState:
    """
    Node 4: Saves the grading result to a JSON file.
    (Later this will save to a database)
    """
    print(f"\n💾 Node 4: Storing result...")
    
    if not state["is_valid"]:
        print("  ⏭️  Skipping — invalid state")
        return state
    
    # Create output folder
    os.makedirs("samples/grading_results", exist_ok=True)
    
    # Build the output record
    output = {
        "student_id": state["student_id"],
        "question_id": state["question_id"],
        "max_marks": state["max_marks"],
        "grading_result": state["grading_result"],
        "status": "AI_GRADED_PENDING_REVIEW"
    }
    
    # Save to file
    filename = f"samples/grading_results/{state['student_id']}_{state['question_id']}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"  ✅ Saved to {filename}")
    return state


# ─────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────
def build_grading_pipeline():
    """Assembles all nodes into a pipeline graph."""
    
    graph = StateGraph(GradingState)
    
    # Add all nodes
    graph.add_node("receive_input", node_receive_input)
    graph.add_node("call_grader", node_call_grader)
    graph.add_node("validate_result", node_validate_result)
    graph.add_node("store_result", node_store_result)
    
    # Connect nodes in order
    graph.set_entry_point("receive_input")
    graph.add_edge("receive_input", "call_grader")
    graph.add_edge("call_grader", "validate_result")
    graph.add_edge("validate_result", "store_result")
    graph.add_edge("store_result", END)
    
    return graph.compile()


# ─────────────────────────────────────────
# TEST THE FULL PIPELINE
# ─────────────────────────────────────────
if __name__ == "__main__":
    
    # Build the pipeline
    pipeline = build_grading_pipeline()
    
    print("🚀 Running Grading Pipeline...")
    print("="*50)
    
    # Sample input (simulating one student, one question)
    initial_state = {
        "student_id": "student_001",
        "question_id": "question_1",
        "question_text": "Explain the OSI model and its layers.",
        "criteria": [
            {"point": "Named all 7 layers correctly", "marks": 3},
            {"point": "Explained function of at least 4 layers", "marks": 4},
            {"point": "Gave a real-world example", "marks": 3}
        ],
        "max_marks": 10,
        "student_answer": """
            The OSI model stands for Open Systems Interconnection.
            It has 7 layers: Physical, Data Link, Network, Transport,
            Session, Presentation, Application.
            The transport layer uses TCP for reliable communication.
            For example HTTP is used in the application layer for web browsing.
        """,
        "grading_result": {},
        "is_valid": False,
        "error": ""
    }
    
    # Run the pipeline
    final_state = pipeline.invoke(initial_state)
    
    # Print final result
    print("\n" + "="*50)
    print("PIPELINE COMPLETE")
    print("="*50)
    result = final_state["grading_result"]
    print(f"Student: {final_state['student_id']}")
    print(f"Question: {final_state['question_id']}")
    print(f"Score: {result['score']}/{final_state['max_marks']}")
    print(f"Justification: {result['justification']}")