from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, quizzes, documents

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(quizzes.router, tags=["quizzes"])
api_router.include_router(documents.router, tags=["documents"])
