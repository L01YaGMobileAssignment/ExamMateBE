from fastapi import APIRouter, HTTPException
from app.schemas.user import User
from app.api.deps import CurrentUser
import app.crud.user as user_crud
from app.core.config import SUPPORTED_LANGUAGES

router = APIRouter()

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: CurrentUser):
    return current_user

@router.put("/users/me/language")
async def update_user(current_user: CurrentUser, language: str):
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Invalid language")
    user_crud.update_user_language(current_user.username, language)
    return {"message": "Language updated successfully."}
