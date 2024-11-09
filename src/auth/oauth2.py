from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
import jwt.utils
from pydantic import EmailStr
from sqlalchemy.orm import Session
import jwt

from . import schemas, models, utils
from .. import users, mail, exceptions, config
from .. database import get_db
from .. config import settings

router = APIRouter(prefix="/auth")

@router.post('/login', status_code=status.HTTP_200_OK, response_model=schemas.AccessToken)
def login(user: schemas.Login, db: Session = Depends(get_db)):
    if(not utils.authenticate_user(username=user.username, password=user.password, db=db)):
        raise exceptions.InvalidCredentials
    payload = schemas.TokenPayload(username=user.username).model_dump()
    token: schemas.AccessToken = utils.create_access_token(to_encode=payload, usage="login", db=db)
    return token

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user = Depends(utils.get_current_user), token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if(not utils.token_in_valid_jwts(token=token, db=db)):
            raise exceptions.InvalidToken
        utils.remove_token_from_valid_jwts(token=token, db=db)
    except jwt.InvalidTokenError:
        raise exceptions.InvalidToken

@router.post('/forgot-password', status_code=status.HTTP_200_OK)
def get_password_reset_link(user: schemas.ForgotPassword, db: Session = Depends(get_db)):
    db_user = db.query(users.models.User).filter(users.models.User.username==user.email).first()
    if(not db_user):
        raise exceptions.ResourceNotFound(detail="Username not found")
    payload = schemas.TokenPayload(username=user.email).model_dump()
    token = utils.create_access_token(to_encode=payload, expire_minutes=settings.password_reset_token_expire_minutes, usage="password_reset", db=db)
    reset_link = f'http://localhost:8000/password-reset/?token={token.token}'
    mail.send_email(
                to=[user.email], 
                subject="Jana Dubai - Password Reset Request", 
                body=f"Follow the link to change your password: {reset_link} . If you think you got this message by mistake, just ignore it.",
    )
    return {"message": f"An email has been sent to {user.email}. Check you inbox or spam folder to reset your password.",
            "token": token.token}
    
@router.post('/reset-password/', status_code=status.HTTP_200_OK)
def change_password(data: schemas.ResetPassword, token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if(not utils.token_in_valid_jwts(token=token, usages="password_reset")):
            raise exceptions.InvalidToken
        username = utils.get_user_from_token(token=data.token, db=db).username
        db_user = db.query(users.models.User).filter(users.models.User.username == username).first()
        if(not db_user):
            raise exceptions.ResourceNotFound(detail="Username not found")
        db_user.password = utils.hash_password(data.password)
        db.commit()
        return {"message": "Password has been changes successfuly"}
    except jwt.InvalidTokenError:
        raise exceptions.InvalidToken