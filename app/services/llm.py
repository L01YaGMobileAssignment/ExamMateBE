from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEYS, MODEL_NAME, VIETNAMESE_LANGUAGE_PROMPT
import traceback

def generate_content(
    file_path: str,
    system_prompt: str,
    language: str = "en",
    generation_config: types.GenerateContentConfig | dict | None = None
) -> str:
    if not GEMINI_API_KEYS:
        raise Exception("GEMINI_API_KEY is not set")

    last_exception = None

    if language == "vi":
        system_prompt = system_prompt + VIETNAMESE_LANGUAGE_PROMPT

    for i, key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"Attempting LLM generation with API key {i+1}/{len(GEMINI_API_KEYS)}")
            client = genai.Client(api_key=key)
            uploaded_file = client.files.upload(file=file_path)
            
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[system_prompt, uploaded_file],
                config=generation_config
            )
            return response.text
        except Exception as e:
            traceback.print_exc()
            print(f"Attempt with API key {i+1} failed: {e}")
            last_exception = e
            continue
    
    raise Exception(f"Failed to generate content after trying all keys. Last error: {str(last_exception)}")
