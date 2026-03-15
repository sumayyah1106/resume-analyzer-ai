import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import ResumeAnalysis, analyze_resume
from config import ALLOWED_EXTENSIONS, APP_TITLE, APP_VERSION, MAX_FILE_SIZE_MB
from resume_parser import parse_plain_text, parse_resume

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Analyze resumes via file upload (PDF/DOCX/TXT) or pasted plain text.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_file(filename: str, size: int):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Use PDF, DOCX, or TXT."
        )
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {MAX_FILE_SIZE_MB} MB."
        )


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": APP_TITLE, "version": APP_VERSION}


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "supported_formats": ALLOWED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE_MB,
    }


@app.post("/analyze-resume", response_model=ResumeAnalysis, tags=["Resume"])
async def analyze_resume_file(file: UploadFile = File(...)):
    """
    Upload a PDF, DOCX, or TXT resume file.
    Postman: Body → form-data → key: file (type: File) → select your resume.
    """
    file_bytes = await file.read()
    _validate_file(file.filename, len(file_bytes))

    try:
        resume_text = parse_resume(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")

    try:
        result = analyze_resume(resume_text)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return result


@app.post("/analyze-text", response_model=ResumeAnalysis, tags=["Resume"])
async def analyze_resume_text(text: str = Form(...)):
    """
    Paste resume text directly.
    Postman: Body → form-data → key: text (type: Text) → paste resume content.
    """
    try:
        resume_text = parse_plain_text(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        result = analyze_resume(resume_text)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return result


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )


