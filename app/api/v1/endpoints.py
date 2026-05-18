from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.database import get_db, AsyncSessionLocal
from app.models.models import Exam, Submission
from app.schemas.schemas import ExamCreate, ExamResponse, GradeOverride
from app.services.ocr_service import OCRService
from app.services.grader_service import GradingService
import json
import shutil
import os

router = APIRouter()

# ──────────────────────────────────────────────────────────────────────
# BACKGROUND TASK WORKER
# ──────────────────────────────────────────────────────────────────────
async def process_and_grade_exam(submission_id: int, file_path: str, rubric: dict, db_session: AsyncSession):
    try:
        print(f"\n🚀 Background pipeline kicked off for Submission ID: {submission_id}")
        
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        ocr_service = OCRService()
        filename = os.path.basename(file_path)
        extracted_text, image_keys = await ocr_service.extract(
            file_bytes=pdf_bytes, 
            rubric=rubric, 
            submission_id=str(submission_id),
            filename=filename
        )
        print("✅ Phase 2 OCR & Question Mapping Complete!")

        grading_service = GradingService()
        final_grades = {}
        total_score = 0.0
        
        for q_id, student_answer in extracted_text.items():
            question_rubric = rubric.get(q_id, {})
            if not question_rubric:
                continue
                
            grade_result = await grading_service.grade_question(
                question_rubric=question_rubric,
                student_answer=student_answer,
                question_id=q_id
            )
            final_grades[q_id] = grade_result
            total_score += float(grade_result.get("score", 0.0))

        print(f"✅ Phase 3 Groq Grading Complete! Total Score: {total_score}")

        result = await db_session.execute(select(Submission).where(Submission.id == submission_id))
        submission = result.scalar_one_or_none()
        
        if submission:
            submission.extracted_text = json.dumps(extracted_text)
            submission.page_image_keys = image_keys
            submission.grading_breakdown = final_grades
            submission.ai_score = total_score
            submission.final_score = total_score
            submission.status = "Completed"
            
            await db_session.commit()
            print(f"💾 Saved grading results to PostgreSQL for Submission {submission_id}!")
            
    except Exception as e:
        print(f"❌ Background pipeline failed: {str(e)}")
        try:
            result = await db_session.execute(select(Submission).where(Submission.id == submission_id))
            submission = result.scalar_one_or_none()
            if submission:
                submission.status = f"Failed: {str(e)}"
                await db_session.commit()
        except Exception:
            pass
    finally:
        await db_session.close()


# ──────────────────────────────────────────────────────────────────────
# API ENDPOINTS
# ──────────────────────────────────────────────────────────────────────
@router.post("/exams", response_model=ExamResponse)
async def create_exam(title: str = Form(...), rubric_str: str = Form(...), db: AsyncSession = Depends(get_db)):
    rubric_json = json.loads(rubric_str)
    new_exam = Exam(title=title, rubric=rubric_json)
    db.add(new_exam)
    await db.flush()
    await db.commit()
    return new_exam

@router.post("/upload-exam/{exam_id}")
async def upload_exam(
    exam_id: int, 
    student_id: str = Form(...), 
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db)
):
    os.makedirs("./uploads", exist_ok=True)
    
    saved_path = f"./uploads/{exam_id}_{student_id}_{file.filename}"
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    
    if not exam:
        return {"error": f"Exam with ID {exam_id} not found"}, 404

    new_submission = Submission(exam_id=exam_id, student_id=student_id, file_path=saved_path, status="Processing")
    db.add(new_submission)
    await db.flush()
    await db.commit()
    
    bg_session = AsyncSessionLocal() 
    background_tasks.add_task(
        process_and_grade_exam, new_submission.id, saved_path, exam.rubric, bg_session
    )

    return {"message": "File uploaded successfully. AI processing initiated.", "submission_id": new_submission.id}

@router.patch("/grades/{submission_id}/override")
async def override_grade(submission_id: int, payload: GradeOverride, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission:
        submission.ta_override_score = payload.ta_override_score
        submission.final_score = payload.ta_override_score
        await db.commit()
        return {"status": "success", "final_score": submission.final_score}
    return {"error": "Submission record not found"}, 404