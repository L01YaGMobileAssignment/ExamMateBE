from fastapi import APIRouter, HTTPException, status
import app.crud.quizzes as quizzes_crud
import app.crud.documents as documents_crud
from app.schemas.quizzes import Quiz, QuizGenerationRequest, GeneratedQuiz
from app.api.deps import CurrentUser
from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEY, MODEL_NAME, QUIZ_SYSTEM_PROMPT

router = APIRouter()

@router.get("/quizzes", response_model=list[Quiz])
async def get_quizzes(current_user: CurrentUser):
    return quizzes_crud.get_quizzes(current_user)

@router.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(current_user: CurrentUser, quiz_id: str):
    return quizzes_crud.get_quiz(quiz_id, current_user)

@router.post("/quizzes/generate", response_model=Quiz)
async def generate_quiz(current_user: CurrentUser, request: QuizGenerationRequest):
    document_id = request.document_id
    
    # Check document details and access
    document = documents_crud.get_document(document_id, current_user.username)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
         
    doc_path = documents_crud.get_document_path(document_id, current_user.username)
    if not doc_path:
        raise HTTPException(status_code=404, detail="File path not found")
        
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
         
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        uploaded_file = client.files.upload(file=doc_path)
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[QUIZ_SYSTEM_PROMPT, uploaded_file],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeneratedQuiz.model_json_schema(),
            },
        )
        
        generated_quiz_data = GeneratedQuiz.model_validate_json(response.text)
        quiz = quizzes_crud.create_quiz(generated_quiz_data, current_user.username)
        return quiz
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
