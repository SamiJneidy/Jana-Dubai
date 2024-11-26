import jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy import and_, update
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import get_db
from ..core.exceptions import *
from fastapi import Depends
from ..core.config import settings, logger
from .. import schemas, models
from ..utils import send_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def token_in_db(db: Session, token: str, usage: str) -> bool:
    db_token: models.ValidJwt = (
        db.query(models.ValidJwt)
        .filter(models.ValidJwt.token == token, models.ValidJwt.usage == usage)
        .first()
    )
    if not db_token:
        return False
    return True


async def validate_token(token: str, db: Session, usage: str = "login") -> None:
    try:
        payload: dict = jwt.decode(
            jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload["username"]
        if not username or not await token_in_db(db=db, token=token, usage=usage):
            raise InvalidToken()
    except jwt.InvalidTokenError:
        raise InvalidToken()


async def get_user_from_token(token: str, db: Session, usage: str) -> schemas.User:
    from . import get_user_by_username

    await validate_token(token=token, usage=usage, db=db)
    payload: dict = jwt.decode(
        jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
    )
    username: str = payload["username"]
    return await get_user_by_username(username=username, db=db)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:
    return await get_user_from_token(token=token, usage="login", db=db)


async def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.User:
    user: schemas.User = await get_user_from_token(token=token, usage="login", db=db)
    if user.role != "ADMIN":
        raise Forbidden()
    return user


async def add_token(token: str, expire_time: datetime, usage: str, db: Session) -> None:
    new_token: models.ValidJwt = models.ValidJwt(
        token=token, expire_time=expire_time, usage=usage
    )
    db.add(new_token)
    db.commit()


async def revoke_token(token: str, db: Session, usage: str = "login") -> None:
    query = db.query(models.ValidJwt).filter(
        models.ValidJwt.token == token, models.ValidJwt.usage == usage
    )
    query.delete()
    db.commit()


async def create_access_token(
    to_encode: dict,
    db: Session,
    expire_minutes=settings.access_token_expire_minutes,
    token_type: str = "bearer",
    usage: str = "login",
) -> schemas.AccessToken:

    expire_time = datetime.now() + timedelta(minutes=expire_minutes)
    to_encode["exp"] = expire_time
    token: str = jwt.encode(
        payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )
    await add_token(token=token, expire_time=expire_time, db=db, usage=usage)
    access_token: schemas.AccessToken = schemas.AccessToken(
        token=token, token_type=token_type
    )
    return access_token


async def get_current_token(token: str = Depends(oauth2_scheme)) -> str:
    return token


async def login(credentials: schemas.Login, db: Session) -> schemas.LoginResponse:
    from . import get_db_user, get_user_by_username

    db_user: models.User = await get_db_user(username=credentials.username, db=db)
    if not verify_password(
        plain_password=credentials.password, hashed_password=db_user.password
    ):
        raise InvalidCredentials()
    payload: schemas.TokenPayload = schemas.TokenPayload(
        username=db_user.username
    ).model_dump()
    token: schemas.AccessToken = await create_access_token(
        to_encode=payload, usage="login", db=db
    )
    user: schemas.User = await get_user_by_username(username=db_user.username, db=db)
    resp: schemas.LoginResponse = schemas.LoginResponse(
        **token.model_dump(), **user.model_dump()
    )
    return resp


async def logout(token: str, db: Session):
    await validate_token(token=token, db=db, usage="login")
    await revoke_token(token=token, db=db, usage="login")


async def signup(data: schemas.UserCreate, db: Session) -> schemas.User:
    from . import user_in_db, get_user_by_username

    if await user_in_db(username=data.username, db=db):
        raise UsernameAlreadyInUse()
    user: models.User = models.User(**data.model_dump())
    user.password = hash_password(user.password)
    db.add(user)
    db.commit()
    return await get_user_by_username(username=data.username, db=db)


async def get_password_reset_link(
    restore_data: schemas.ForgotPassword, host_url: str, db: Session
):
    from . import user_in_db

    if not await user_in_db(db=db, username=restore_data.email):
        raise UserNotFound()
    payload: dict = schemas.TokenPayload(username=restore_data.email).model_dump()
    token: schemas.AccessToken = await create_access_token(
        to_encode=payload,
        expire_minutes=settings.password_reset_token_expire_minutes,
        usage="password reset",
        db=db,
    )
    reset_link: str = f"{host_url}reset-password/?token={token.token}"
    await send_email(
        to=[restore_data.email],
        subject="Jana Dubai - Password Reset Request",
        body=f"Please follow the link to reset your password: {reset_link} . If you think you got this message by mistake, just ignore it.",
    )
    return {
        "message": f"An email has been sent to {restore_data.email}. Check you inbox or spam folder to reset your password."
    }


async def reset_password(data: schemas.ResetPassword, db: Session):
    try:
        await validate_token(token=data.token, usage="password reset", db=db)
        user: schemas.User = await get_user_from_token(
            token=data.token, usage="password reset", db=db
        )
        hashed_password: str = hash_password(data.password)
        db.execute(
            update(models.User)
            .where(models.User.username == user.username)
            .values(password=hashed_password)
        )
        db.commit()
        return {"message": "Password has been reset successfully"}
    except jwt.InvalidTokenError:
        raise InvalidToken()
