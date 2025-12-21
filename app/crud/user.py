from app.schemas.user import UserInDB, UserCreate
from app.core.security import verify_password, get_password_hash
from app.db.database import get_db_connection

def get_user(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return UserInDB(**dict(row))
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password, disabled) VALUES (?, ?, ?, ?, ?)",
            (user.username, user.email, user.full_name, hashed_password, False),
        )
        conn.commit()
    return get_user(user.username)
