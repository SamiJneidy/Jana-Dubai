from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, time
class User(BaseModel):
    username: EmailStr
    phone: Optional[str] = None
    role: Optional[str] = "CUSTOMER"
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: EmailStr
    password: str
    phone: Optional[str] = None
    role: Optional[str] = "CUSTOMER"
    onblacklist: Optional[bool] = False


class UserUpdate(BaseModel):
    username: EmailStr
    old_password: str
    new_password: str
    phone: Optional[str] = None
