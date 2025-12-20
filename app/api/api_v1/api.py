from fastapi import APIRouter
from app.api.api_v1.endpoints import login, users, quizzes, documents

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(quizzes.router, tags=["quizzes"])
api_router.include_router(documents.router, tags=["documents"])
