import os
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

UPLOAD_DIR = Path("user_upload")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
