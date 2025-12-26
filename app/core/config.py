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
QUIZ_SYSTEM_PROMPT = """**Role:** You are an Expert Assessment Specialist. Your goal is to create high-quality multiple-choice quizzes based on provided documentation.

**Task:** Generate a `{num_questions}`-question quiz that accurately tests comprehension of the provided document.

**Guidelines for Quality:**

1. **Clarity:** Questions must be concise and avoid "all of the above" or "none of the above" options.
2. **Plausibility:** Incorrect options (distractors) should be plausible and based on information within the text, rather than being obviously wrong.
3. **Single Best Answer:** Ensure there is only one clearly correct answer based on the document.
4. **Explanations:** The `why_correct` field must explain *why* the answer is right and, if helpful, why other distractors are wrong, referencing the context, short and concise.
5. **Indexing:** The `answer_index` must be **0-indexed** (e.g., if the first option is correct, the index is 0).
6. **Coverage:** Distribute questions across the entire document rather than focusing only on the first few paragraphs.
"""