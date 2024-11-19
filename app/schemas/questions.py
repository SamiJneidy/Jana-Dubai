from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Question(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str
    answered: bool
    created_at: datetime

class CreateQuestion(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str


class AnswerQuestion(BaseModel):
    id: int
    message: str
