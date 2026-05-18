"""
app/services/grader_service.py
Standardized: Groq LLM Grader Integration
"""
import os
import httpx
from app.config import settings

class GradingService:
    def __init__(self):
        # Fallback to a placeholder string if GROQ_API_KEY isn't initialized yet
        self.api_key = getattr(settings, "GROQ_API_KEY", "mock_key")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def grade_question(self, question_rubric: dict, student_answer: str, question_id: str) -> dict:
        print(f"🤖 Sending {question_id} to Groq AI Grader...")
        
        # Build a robust system prompt for Llama 3.3
        system_prompt = (
            "You are an expert academic evaluator. Grade the student's answer strictly based on the provided rubric. "
            "Return your final response ONLY as a valid JSON object with two keys: "
            "'score' (a float value) and 'feedback' (a brief explanation of marks awarded or deducted)."
        )
        
        user_prompt = f"Rubric Criteria:\n{question_rubric}\n\nStudent Answer:\n{student_answer}"
        
        # Mock responses if no real API key is detected so your terminal never crashes
        if not self.api_key or self.api_key == "mock_key":
            print("⚠️ No Groq API Key found. Simulating an automatic grade...")
            return {"score": 8.5, "feedback": "Good attempt. Met most criteria perfectly."}

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=30.0)
                
            if response.status_code == 200:
                result_json = response.json()
                content_str = result_json["choices"][0]["message"]["content"]
                import json
                return json.loads(content_str)
            else:
                print(f"❌ Groq API returned error status: {response.status_code}")
                return {"score": 0.0, "feedback": f"API Error status code {response.status_code}."}
                
        except Exception as e:
            print(f"❌ Grading connection failed: {str(e)}")
            return {"score": 0.0, "feedback": f"Grading process exception: {str(e)}"}