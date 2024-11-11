from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

from . import models, schemas
from .. import exceptions, users
from ..database import get_db
from .. config import settings

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_from_db(username: str, db: Session):
    try:
        user = db.query(users.models.User).filter(users.models.User.username == username).first()
        return user
    except:
        raise exceptions.ResourceNotFound
    
def password_is_valid(password: str) -> bool:
    different_chars: set = {}
    for c in password:
        different_chars.add(c)
    if(len(password) < 8 or len(different_chars) < 3):
        return False
    return True

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db: Session) -> bool:
    db_user = db.query(users.models.User).filter(users.models.User.username == username).first()
    if(not db_user or not verify_password(password, db_user.password)):
        return False
    return True

def get_user_role(username: str, db: Session):
    role = db.execute(
        select(users.models.User.role).
        where(users.models.User.username == username)
        ).fetchone()[0]
    return role

def add_token_to_valid_jwts(token: str, expire_time: datetime, usage: str, db: Session):
    new_token: models.ValidJwt = models.ValidJwt(token=token, expire_time=expire_time, usage=usage)
    db.add(new_token)
    db.commit()

def remove_token_from_valid_jwts(token: str, db: Session, usage: str = "login"):
    to_delete: schemas.AccessToken = db.query(models.ValidJwt).filter(models.ValidJwt.token==token and models.ValidJwt.usage == usage).first()
    db.delete(to_delete)
    db.commit()

def token_in_valid_jwts(token: str, db: Session, usage: str = "login") -> bool:
    if(db.query(models.ValidJwt).filter(models.ValidJwt.token == token and models.ValidJwt.usage == usage).first()):
        return True
    return False

def create_access_token(to_encode: dict, expire_minutes = settings.access_token_expire_minutes, token_type: str = "bearer", usage: str = "login", db: Session = None) -> schemas.AccessToken:
    expire_time = datetime.now() + timedelta(minutes=expire_minutes)
    to_encode["exp"] = expire_time
    token = jwt.encode(payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm)
    add_token_to_valid_jwts(token=token, expire_time=expire_time, db=db, usage=usage)
    access_token = schemas.AccessToken(token=token, token_type=token_type)
    return access_token

def get_current_token(token: str = Depends(oauth2_scheme)) -> str:
    return token

def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(jwt=token, key=settings.secret_key, algorithms=[settings.algorithm])
        user = users.schemas.User(username=payload["username"])
        if(not user or not token_in_valid_jwts(token=token, db=db)):
            raise exceptions.InvalidToken
        return user
    except jwt.InvalidTokenError:
        raise exceptions.InvalidToken

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> users.schemas.User:
    try:
        payload = jwt.decode(jwt=token, key=settings.secret_key, algorithms=[settings.algorithm])
        current_user = users.schemas.User(username=payload["username"])
        if(not current_user or not token_in_valid_jwts(token=token, db=db)):
            raise exceptions.InvalidToken
        return current_user
    except jwt.InvalidTokenError:
        raise exceptions.InvalidToken
    
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> users.schemas.User:
    try:
        payload = jwt.decode(jwt=token, key=settings.secret_key, algorithms=[settings.algorithm])
        current_user = users.schemas.User(username=payload["username"])
        if(not current_user or not token_in_valid_jwts(token=token, db=db)):
            raise exceptions.InvalidToken
        if get_user_role(username=payload["username"], db=db) != "ADMIN":
            raise exceptions.Forbidden
        return current_user
    except jwt.InvalidTokenError:
        raise exceptions.InvalidToken


    