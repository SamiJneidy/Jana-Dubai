from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class TokenPayload(BaseModel):
    username: str = None

class AccessToken(BaseModel):
    token: str
    token_type: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    password: str