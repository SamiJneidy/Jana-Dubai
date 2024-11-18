from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Question(BaseModel):
    id: int
    email: EmailStr
    name: str
    phone: str
    company: str
    message: str
    answered: bool
    created_at: datetime

class CreateQuestion(BaseModel):
    email: EmailStr
    name: Optional[str] = ""
    phone: Optional[str] = ""
    company: Optional[str] = ""
    message: str
