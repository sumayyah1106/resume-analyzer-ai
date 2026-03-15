import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

APP_TITLE: str = "AI Resume Analyzer"
APP_VERSION: str = "1.0.0"
MAX_FILE_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]