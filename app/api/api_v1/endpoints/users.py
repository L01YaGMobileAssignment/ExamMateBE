from fastapi import APIRouter
from app.schemas.user import User
from app.api.deps import CurrentUser

router = APIRouter()

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: CurrentUser):
    return current_user


