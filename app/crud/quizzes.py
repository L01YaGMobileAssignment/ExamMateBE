import json
from app.schemas.quizzes import Quiz
from app.schemas.user import User
from app.db.database import get_db_connection

def get_quizzes(current_user: User):
    quizzes = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE owned_by = ? OR access = 'public'", (current_user.username,))
        quiz_rows = cursor.fetchall()

        for quiz_row in quiz_rows:
            quiz_data = dict(quiz_row)
            # Get questions
            cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_data["quiz_id"],))
            question_rows = cursor.fetchall()
            questions = []
            for q_row in question_rows:
                q_data = dict(q_row)
                q_data["options"] = json.loads(q_data["options"])
                questions.append(q_data)
            
            quiz_data["questions"] = questions
            quizzes.append(Quiz(**quiz_data))
    return quizzes

def get_quiz(quiz_id: str, current_user: User):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check if quiz exists and is accessible
        cursor.execute("SELECT * FROM quizzes WHERE quiz_id = ?", (quiz_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        quiz_data = dict(row)
        if quiz_data["owned_by"] != current_user.username and quiz_data["access"] != "public":
            return None
        
        # Get questions
        cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
        question_rows = cursor.fetchall()
        questions = []
        for q_row in question_rows:
            q_data = dict(q_row)
            q_data["options"] = json.loads(q_data["options"])
            questions.append(q_data)
            
        quiz_data["questions"] = questions
        return Quiz(**quiz_data)
    return None
