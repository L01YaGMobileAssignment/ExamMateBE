from pydantic import BaseModel

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    answer_index: int
    correct_answer: str
    why_correct: str
    created_at: int | None = None

class QuizBase(BaseModel):
    quiz_id: str
    owned_by: str
    quiz_title: str
    created_at: int | None = None

class Quiz(QuizBase):
    questions: list[QuizQuestion]

class GeneratedQuestion(BaseModel):
    question: str
    options: list[str]
    answer_index: int
    why_correct: str

class GeneratedQuiz(BaseModel):
    title: str
    questions: list[GeneratedQuestion]

class QuizGenerationRequest(BaseModel):
    document_id: str
    num_questions: int = 10
