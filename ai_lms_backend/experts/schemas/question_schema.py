from pydantic import BaseModel, Field
from typing import List


class QuestionItem(BaseModel):
    stem: str
    options: List[str] | None = None
    answer: str
    explanation: str


class QuestionOutput(BaseModel):
    topic: str
    difficulty: str = Field(..., enum=["easy", "medium", "hard"])
    questions: List[QuestionItem]