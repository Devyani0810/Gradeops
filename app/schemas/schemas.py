from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ExamCreate(BaseModel):
    title: str
    rubric: Dict[str, Any]

class ExamResponse(BaseModel):
    id: int
    title: str
    rubric: Dict[str, Any]
    created_at: datetime
    class Config:
        from_attributes = True

class GradeOverride(BaseModel):
    ta_override_score: float