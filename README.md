# GradeOps v1.5
AI-powered exam grading system for handwritten answer sheets.

## Architecture
- **Backend**: FastAPI + SQLite + SQLAlchemy
- **Frontend**: React
- **AI**: LangChain + OpenAI GPT

## Setup
### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
### Frontend
```bash
cd frontend
npm install
npm start
```

## Features
- Upload student answer sheet PDFs
- OCR extraction using PyMuPDF + Tesseract
- AI grading via LangChain agent pipeline
- TA review dashboard
- Grade override support
