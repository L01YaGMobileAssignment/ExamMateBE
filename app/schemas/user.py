from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class User(UserBase):
    created_at: int | None = None

class UserInDB(User):
    hashed_password: str
    disabled: bool | None = None

class UserCreate(UserBase):
    password: str
