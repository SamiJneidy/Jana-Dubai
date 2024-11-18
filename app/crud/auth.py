import jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy import and_, update
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import get_db
from ..core.exceptions import *
from fastapi import Depends
from ..core.config import settings
from .. import schemas, models
from ..utils import send_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def validate_token(token: str, db: Session, usage: str = "login") -> None:
    try:
        payload = jwt.decode(
            jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload["username"]
        if (
            not username
            or not db.query(models.ValidJwt)
            .filter(
                and_(models.ValidJwt.token == token, models.ValidJwt.usage == usage)
            )
            .first()
        ):
            raise InvalidToken()
    except jwt.InvalidTokenError:
        raise InvalidToken()
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_user_from_token(token: str, db: Session, usage: str) -> schemas.User:
    validate_token(token=token, usage=usage, db=db)
    from . import get_user_by_username

    payload = jwt.decode(
        jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
    )
    username: str = payload["username"]
    return get_user_by_username(username=username, db=db)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:
    get_user_from_token(token=token, usage="login", db=db)


def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:
    user: schemas.User = get_user_from_token(token=token, usage="login", db=db)
    if user.role != "ADMIN":
        raise Forbidden()
    return user


def add_token(token: str, expire_time: datetime, usage: str, db: Session) -> None:
    try:
        new_token: models.ValidJwt = models.ValidJwt(
            token=token, expire_time=expire_time, usage=usage
        )
        db.add(new_token)
        db.commit()
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def revoke_token(token: str, db: Session, usage: str = "login") -> None:
    try:
        to_delete: schemas.AccessToken = (
            db.query(models.ValidJwt)
            .filter(models.ValidJwt.token == token and models.ValidJwt.usage == usage)
            .first()
        )
        db.delete(to_delete)
        db.commit()
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


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
            db.query(models.User)
            .filter(models.User.username == credentials.username)
            .first()
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
    validate_token(token=token, db=db)
    revoke_token(token=token, db=db)


def signup(data: schemas.UserCreate, db: Session) -> schemas.User:
    try:
        if db.query(models.User).filter(models.User.username == data.username).first():
            raise ResourceAlreadyInUse()
        user: models.User = models.User(**data.model_dump())
        user.password = hash_password(user.password)
        db.add(user)
        db.commit()
        user = schemas.User(
            **db.query(models.User)
            .filter(models.User.username == data.username)
            .first()
            .to_dict()
        )
        return user
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_password_reset_link(user: schemas.ForgotPassword, host_url: str, db: Session):
    try:
        db_user: models.User = (
            db.query(models.User).filter(models.User.username == user.email).first()
        )
        if not db_user:
            raise UserNotFound()
        payload: dict = schemas.TokenPayload(username=user.email).model_dump()
        token: schemas.AccessToken = create_access_token(
            to_encode=payload,
            expire_minutes=settings.password_reset_token_expire_minutes,
            usage="password reset",
            db=db,
        )
        #reset_link: str = f"{host_url}reset-password/?token={token.token}"
        reset_link: str = f"http://127.0.0.1/reset-password/?token={token.token}"
        send_email(
            to=[user.email],
            subject="Jana Dubai - Password Reset Request",
            body=f"Please follow the link to reset your password: {reset_link} . If you think you got this message by mistake, just ignore it.",
        )
        print(token)
        return {
            "message": f"An email has been sent to {user.email}. Check you inbox or spam folder to reset your password."
        }
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def reset_password(data: schemas.ResetPassword, db: Session):
    try:
        validate_token(token=data.token, usage="password reset", db=db)
        user = get_user_from_token(token=data.token, usage="password reset", db=db)
        hashed_password = hash_password(data.password)
        db.execute(
            update(models.User)
            .where(models.User.username == user.username)
            .values(password=hashed_password)
        )
        db.commit()
        return {"message": "Password has been successfuly reset"}
    except jwt.InvalidTokenError:
        raise InvalidToken()
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()
