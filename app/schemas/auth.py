from pydantic import BaseModel
from .users import User


class TokenPayload(BaseModel):
    username: str = None


class AccessToken(BaseModel):
    token: str
    token_type: str


class Login(BaseModel):
    username: str
    password: str


class LoginResponse(User, AccessToken):
    pass


class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    token: str
    password: str
