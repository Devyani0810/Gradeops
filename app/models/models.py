from sqlalchemy import String, Integer, ForeignKey, Text, JSON, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="TA")

class Exam(Base):
    __tablename__ = "exams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rubric: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Processing")
    
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    ai_score: Mapped[float] = mapped_column(Float, nullable=True)
    ai_justification: Mapped[str] = mapped_column(Text, nullable=True)
    
    ta_override_score: Mapped[float] = mapped_column(Float, nullable=True)
    final_score: Mapped[float] = mapped_column(Float, nullable=True)
    is_plagiarized: Mapped[bool] = mapped_column(Boolean, default=False)