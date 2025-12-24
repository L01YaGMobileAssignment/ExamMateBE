fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}

fake_quizzes_db =[
  {
    "quiz_id": "math_101",
    "owned_by": "johndoe",
    "access": "private",
    "quiz_title": "Basic Mathematics",
    "questions": [
      {
        "id": "q1",
        "question": "What is the square root of 144?",
        "options": ["10", "12", "14", "16"],
        "answer_index": 1,
        "correct_answer": "12"
      },
      {
        "id": "q2",
        "question": "Which of these numbers is a prime number?",
        "options": ["9", "15", "17", "21"],
        "answer_index": 2,
        "correct_answer": "17"
      }
    ]
  },
  {
    "quiz_id": "hist_202",
    "owned_by": "notjohndoe",
    "access": "public",
    "quiz_title": "World History",
    "questions": [
      {
        "id": "q1",
        "question": "In which year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "answer_index": 2,
        "correct_answer": "1945"
      },
      {
        "id": "q2",
        "question": "Who was the first President of the United States?",
        "options": ["Thomas Jefferson", "Abraham Lincoln", "John Adams", "George Washington"],
        "answer_index": 3,
        "correct_answer": "George Washington"
      }
    ]
  }
]