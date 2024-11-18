import jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import get_db
from ..core.exceptions import *
from fastapi import Depends
from ..core.config import settings
from .. import schemas, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:

    try:
        from . import get_user_by_username
        payload = jwt.decode(
            jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload["username"]
        if not username or not validate_token(token=token, db=db):
            raise InvalidToken()
        return get_user_by_username(username=username, db=db)
    except jwt.InvalidTokenError:
        raise InvalidToken()


def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:

    try:
        from . import get_user_by_username
        payload = jwt.decode(
            jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload["username"]
        if not username or not validate_token(token=token, db=db):
            raise InvalidToken
        user: schemas.User = get_user_by_username(username=username, db=db)
        if user.role != "ADMIN":
            raise Forbidden
        return get_user_by_username(username=username, db=db)
    except jwt.InvalidTokenError:
        raise InvalidToken


def add_token(token: str, expire_time: datetime, usage: str, db: Session) -> None:
    new_token: models.ValidJwt = models.ValidJwt(
        token=token, expire_time=expire_time, usage=usage
    )
    db.add(new_token)
    db.commit()


def revoke_token(token: str, db: Session, usage: str = "login") -> None:
    to_delete: schemas.AccessToken = (
        db.query(models.ValidJwt)
        .filter(models.ValidJwt.token == token and models.ValidJwt.usage == usage)
        .first()
    )
    db.delete(to_delete)
    db.commit()


def validate_token(token: str, db: Session, usage: str = "login") -> bool:
    if (
        db.query(models.ValidJwt)
        .filter(and_(models.ValidJwt.token == token, models.ValidJwt.usage == usage))
        .first()
    ):
        return True
    return False


def create_access_token(
    to_encode: dict,
    db: Session,
    expire_minutes=settings.access_token_expire_minutes,
    token_type: str = "bearer",
    usage: str = "login",
) -> schemas.AccessToken:
    expire_time = datetime.now() + timedelta(minutes=expire_minutes)
    to_encode["exp"] = expire_time
    token = jwt.encode(
        payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )
    add_token(token=token, expire_time=expire_time, db=db, usage=usage)
    access_token = schemas.AccessToken(token=token, token_type=token_type)
    return access_token


def get_current_token(token: str = Depends(oauth2_scheme)) -> str:
    return token


def login(credentials: schemas.Login, db: Session) -> schemas.LoginResponse:
    try:
        from . import get_user_by_username
        db_user = (
            db.query(models.User).filter(models.User.username == credentials.username).first()
        )
        if not db_user:
            raise UserNotFound()
        if not verify_password(
            plain_password=credentials.password, hashed_password=db_user.password
        ):
            raise InvalidCredentials()
        payload = schemas.TokenPayload(username=db_user.username).model_dump()
        token: schemas.AccessToken = create_access_token(
            to_encode=payload, usage="login", db=db
        )
        user: schemas.User = get_user_by_username(username=db_user.username, db=db)
        resp = schemas.LoginResponse(**token.model_dump(), **user.model_dump())
        return resp
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def logout(token: str, db: Session):
    try:
        if not validate_token(token=token, db=db):
            raise InvalidToken
        revoke_token(token=token, db=db)
    except DatabaseError as e:
        raise UnexpectedError() from e


def signup(data: schemas.UserCreate, db: Session) -> schemas.User:
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise ResourceAlreadyInUse
    db_user: models.User = models.User(**data.model_dump())
    db_user.password = hash_password(db_user.password)
    db.add(db_user)
    db.commit()
    user = schemas.User(
        **db.query(models.User)
        .filter(models.User.username == data.username)
        .first()
        .to_dict()
    )
    return user


# def get_password_reset_link(user: schemas.ForgotPassword, db: Session):
#     try:
#     db_user = db.query(models.User).filter(models.User.username==user.email).first()
#     if(not db_user):
#         raise ResourceNotFound(detail="Username not found")
#     payload = schemas.TokenPayload(username=user.email).model_dump()
#     token = create_access_token(to_encode=payload, expire_minutes=settings.password_reset_token_expire_minutes, usage="password_reset", db=db)
#     reset_link = f'http://localhost:8000/password-reset/?token={token.token}'
#     mail.send_email(
#                 to=[user.email],
#                 subject="Jana Dubai - Password Reset Request",
#                 body=f"Follow the link to change your password: {reset_link} . If you think you got this message by mistake, just ignore it.",
#     )
#     return {"message": f"An email has been sent to {user.email}. Check you inbox or spam folder to reset your password.",
#             "token": token.token}

# def change_password(data: schemas.ResetPassword, token: str, db: Session):
#     try:
#         if(not token_in_valid_jwts(token=token, usages="password_reset")):
#             raise InvalidToken
#         username = get_user_from_token(token=data.token, db=db).username
#         db_user = db.query(models.User).filter(models.User.username == username).first()
#         if(not db_user):
#             raise ResourceNotFound(detail="Username not found")
#         db_user.password = hash_password(data.password)
#         db.commit()
#         return {"message": "Password has been changes successfuly"}
#     except jwt.InvalidTokenError:
#         raise InvalidToken
