from typing import Optional
from pydantic import BaseModel, EmailStr


class Email(BaseModel):
    to: EmailStr 
    subject: str 
    body: str
    subtype: Optional[str] = "plain"
