from app.schemas.schedule import ScheduleInDB, Schedule
from app.schemas.user import User
from app.db.database import get_db_connection
import time
import uuid


def get_schedule(current_user: User) -> list[ScheduleInDB]:
    schedules = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schedule WHERE owned_by = ?", (current_user.username,))
        schedule_rows = cursor.fetchall()

        for schedule_row in schedule_rows:
            schedules.append(ScheduleInDB(**schedule_row))
    return schedules

def get_schedule_by_id(current_user: User, schedule_id: str) -> ScheduleInDB | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schedule WHERE id = ? AND owned_by = ?", (schedule_id, current_user.username))
        row = cursor.fetchone()
        if not row:
            return None
        return ScheduleInDB(**row)
    return None

def create_schedule(current_user: User, request: Schedule) -> ScheduleInDB:
    current_time = int(time.time())
    schedule_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schedule (id, owned_by, title, description, start_date, end_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (schedule_id, current_user.username, request.title, request.description, request.start_date, request.end_date, current_time, current_time))
        conn.commit()

        cursor.execute("SELECT * FROM schedule WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()

    return ScheduleInDB(**row)

def update_schedule(current_user: User, schedule_id: str, request: Schedule) -> ScheduleInDB:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE schedule
            SET title = ?, description = ?, start_date = ?, end_date = ?, updated_at = ?
            WHERE id = ? AND owned_by = ?
        """, (request.title, request.description, request.start_date, request.end_date, int(time.time()), schedule_id, current_user.username))
        conn.commit()
        
        cursor.execute("SELECT * FROM schedule WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()
    return ScheduleInDB(**row)

def delete_schedule(current_user: User, schedule_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedule WHERE id = ? AND owned_by = ?", (schedule_id, current_user.username))
        conn.commit()
    return None