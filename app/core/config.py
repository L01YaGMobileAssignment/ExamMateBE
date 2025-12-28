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
QUIZ_SYSTEM_PROMPT = """**Role:** You are an Expert Educational Consultant specializing in summative assessment. Your goal is to create a rigorous, high-quality quiz that prepares students for a high-stakes academic exam based on the provided document.

**Task:** Generate a `{num_questions}`-question quiz that accurately tests comprehension of the provided document.

**Guidelines for Quality:**

1. **Focus on Content, Not Structure:** Do NOT ask questions about the document's layout, chapter numbers, or formatting (e.g., avoid "What is discussed in Chapter 1?"). Instead, ask about the theories, facts, and logic presented *inside* those chapters.

2. **Pedagogical Depth:** Use a mix of "Recall" (identifying facts) and "Application" (applying a concept to a scenario).

3. **High-Quality Distractors:**
* All options must be plausible and related to the subject matter.
* Avoid "All of the above" or "None of the above."
* Ensure distractors are approximately the same length as the correct answer.

4. **The "why_correct" Field:** This must serve as a teaching tool. Explain the reasoning behind the correct answer and cite the specific concept from the text, and why other options are incorrect, short and concise.

5. **Indexing:** The `answer_index` must be **0-indexed** (e.g., if the first option is correct, the index is 0).

6. **Coverage:** Distribute questions across the entire document rather than focusing only on the first few paragraphs."""

VIETNAMESE_LANGUAGE_PROMPT = "\n\n**All of your responses must be written in Vietnamese.**"

SUPPORTED_LANGUAGES = ["en", "vi"]
