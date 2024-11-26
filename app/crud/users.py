from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import schemas, models
from ..core.exceptions import *
from ..core.config import logger


async def get_db_user(db: Session, id: int = None, username: str = None) -> models.User:
    db_user: models.User
    if id:
        db_user = db.query(models.User).filter(models.User.id == id).first()
    if username:
        db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise UserNotFound()
    return db_user


async def user_in_db(db: Session, id: int = None, username: str = None) -> bool:
    cnt: int = 0
    if id:
        cnt = db.query(models.User).filter(models.User.id == id).count()
    if username:
        cnt = db.query(models.User).filter(models.User.username == username).count()
    if cnt:
        True
    return False


async def get_user_by_id(id: int, db: Session) -> schemas.User:
    db_user: models.User = await get_db_user(id=id, db=db)
    return schemas.User(**db_user.to_dict())


async def get_all_users(db: Session) -> list[schemas.User]:
    return [
        schemas.User(**db_user.to_dict()) for db_user in db.query(models.User).all()
    ]


async def get_user_by_username(username: str, db: Session) -> schemas.User:
    db_user: models.User = await get_db_user(username=username, db=db)
    return schemas.User(**db_user.to_dict())


async def get_user_role_by_username(username: str, db: Session) -> str:
    db_user: models.User = await get_db_user(username=username, db=db)
    return db_user.role
