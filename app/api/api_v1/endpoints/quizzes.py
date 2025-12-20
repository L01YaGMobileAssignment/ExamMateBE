from fastapi import APIRouter
import app.crud.quizzes as quizzes_crud
from app.schemas.quizzes import Quiz
from app.api.deps import CurrentUser

router = APIRouter()

@router.get("/quizzes", response_model=list[Quiz])
async def get_quizzes(current_user: CurrentUser):
    return quizzes_crud.get_quizzes(current_user)

@router.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(current_user: CurrentUser, quiz_id: str):
    return quizzes_crud.get_quiz(quiz_id, current_user)
