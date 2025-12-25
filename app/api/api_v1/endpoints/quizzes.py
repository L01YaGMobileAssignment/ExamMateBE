from fastapi import APIRouter, HTTPException, status
import app.crud.quizzes as quizzes_crud
import app.crud.documents as documents_crud
from app.schemas.quizzes import Quiz, QuizGenerationRequest, GeneratedQuiz, QuizBase
from app.api.deps import CurrentUser
from app.core.config import QUIZ_SYSTEM_PROMPT
from app.services.llm import generate_content

router = APIRouter()

@router.get("/quizzes", response_model=list[QuizBase])
async def get_quizzes(current_user: CurrentUser):
    return quizzes_crud.get_quizzes(current_user)

@router.get("/quizzes/search", response_model=list[QuizBase])
async def search_quizzes(current_user: CurrentUser, q: str):
    return quizzes_crud.search_quizzes(current_user, q)

@router.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(current_user: CurrentUser, quiz_id: str):
    quiz = quizzes_crud.get_quiz(quiz_id, current_user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/quizzes/generate", response_model=Quiz)
async def generate_quiz(current_user: CurrentUser, request: QuizGenerationRequest):
    document_id = request.document_id
    num_questions = request.num_questions
    
    # Check document details and access
    document = documents_crud.get_document(document_id, current_user.username)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
         
    doc_path = documents_crud.get_document_path(document_id, current_user.username)
    if not doc_path:
        raise HTTPException(status_code=404, detail="File path not found")
        
    try:
        response_text = generate_content(
            file_path=doc_path,
            system_prompt=QUIZ_SYSTEM_PROMPT.format(num_questions=num_questions),
            generation_config={
                "response_mime_type": "application/json",
                "response_json_schema": GeneratedQuiz.model_json_schema(),
            }
        )
        
        generated_quiz_data = GeneratedQuiz.model_validate_json(response_text)
        quiz = quizzes_crud.create_quiz(generated_quiz_data, current_user.username)
        return quiz
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process generated quiz: {str(e)}")
