from fastapi import APIRouter
from app.api.v1.endpoints import router as exams_router

api_router = APIRouter()
api_router.include_router(exams_router)
