from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import schemas, models
from ..core.exceptions import *
from ..core.config import logger

async def get_user_by_id(id: int, db: Session) -> schemas.User:
    try:
        db_user: models.User = (
            db.query(models.User).filter(models.User.id == id).first()
        )
        if not db_user:
            raise UserNotFound()
        user = schemas.User(**db_user.to_dict())
        return user
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise e


async def get_all_users(db: Session) -> list[schemas.User]:
    try:
        results = [
            schemas.User(**db_user.to_dict()) for db_user in db.query(models.User).all()
        ]
        return results
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise e


async def get_user_by_username(username: str, db: Session) -> schemas.User:
    try:
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if not db_user:
            raise UserNotFound()
        user = schemas.User(**db_user.to_dict())
        return user
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def get_user_role_by_username(username: str, db: Session):
    try:
        role = db.execute(
            select(models.User.role).where(models.User.username == username)
        ).fetchone()[0]
        if not role:
            raise UserNotFound()
        return role
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise e
