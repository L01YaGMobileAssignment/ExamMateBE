import os
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

UPLOAD_DIR = Path("user_upload")
ALLOWED_EXTENSIONS = {".pdf"}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"
SUMMARY_SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following document in one paragraph, about 200 words, format it in raw text, do not format it in markdown."
QUIZ_SYSTEM_PROMPT = "Generate a 5 questions multiple choice quiz based on the following document."