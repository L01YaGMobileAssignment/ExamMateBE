import os
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

UPLOAD_DIR = Path("user_upload")
ALLOWED_EXTENSIONS = {".pdf"}
 
GEMINI_API_KEYS = []
if os.getenv("GEMINI_API_KEY"):
    GEMINI_API_KEYS.append(os.getenv("GEMINI_API_KEY"))
if os.getenv("GEMINI_API_KEY2"):
    GEMINI_API_KEYS.append(os.getenv("GEMINI_API_KEY2"))
if os.getenv("GEMINI_API_KEY3"):
    GEMINI_API_KEYS.append(os.getenv("GEMINI_API_KEY3"))

MODEL_NAME = os.getenv("MODEL_NAME")
SUMMARY_SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following document in one paragraph, about 200 words, format it in raw text, do not format it in markdown."
QUIZ_SYSTEM_PROMPT = "Generate a {num_questions} questions multiple choice quiz based on the following document."