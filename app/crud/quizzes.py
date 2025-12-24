import json
import uuid
import time
from app.schemas.quizzes import Quiz, GeneratedQuiz
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

def create_quiz(quiz_data: GeneratedQuiz, owner: str) -> Quiz:
    quiz_id = str(uuid.uuid4())
    access = "private"
    current_time = int(time.time())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO quizzes (quiz_id, owned_by, access, quiz_title, created_at) VALUES (?, ?, ?, ?, ?)",
                       (quiz_id, owner, access, quiz_data.title, current_time))
        
        questions = []
        for q in quiz_data.questions:
            q_id = str(uuid.uuid4())
            if 0 <= q.answer_index < len(q.options):
                 correct_answer = q.options[q.answer_index]
            else:
                 correct_answer = "" 
            
            cursor.execute("""
                INSERT INTO questions (quiz_id, id, question, options, answer_index, correct_answer, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quiz_id, q_id, q.question, json.dumps(q.options), q.answer_index, correct_answer, current_time))
            
            questions.append({
                "id": q_id,
                "question": q.question,
                "options": q.options,
                "answer_index": q.answer_index,
                "correct_answer": correct_answer,
                "created_at": current_time
            })
        
        conn.commit()
    
    return Quiz(
        quiz_id=quiz_id,
        owned_by=owner,
        quiz_title=quiz_data.title,
        questions=questions,
        created_at=current_time
    )

