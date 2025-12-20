from pydantic import BaseModel

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    answer_index: int
    correct_answer: str

class Quiz(BaseModel):
    quiz_id: str
    owned_by: str
    quiz_title: str
    questions: list[QuizQuestion]