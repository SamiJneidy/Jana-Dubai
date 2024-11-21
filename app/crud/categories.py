from sqlalchemy import insert, or_, select
from sqlalchemy.orm import Session


from .. import models, schemas
from ..core.exceptions import *
from ..core.config import logger


async def get_category_by_id(id: int, db: Session) -> schemas.Category:
    try:
        db_category = db.query(models.Category).filter(models.Category.id == id).first()
        if not db_category:
            raise CategoryNotFound()
        category: schemas.Category = schemas.Category(**db_category.to_dict())
        return category
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def get_all_categories(db: Session, type: str = None) -> list[schemas.Category]:
    try:
        results = [
            schemas.Category(**db_category.to_dict())
            for db_category in db.query(models.Category)
            .filter(or_(type is None, models.Category.type == type))
            .all()
        ]
        return results
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def create_category(data: schemas.CategoryCreate, db: Session) -> schemas.Category:
    try:
        id: int = db.execute(
            insert(models.Category)
            .values(**data.model_dump())
            .returning(models.Category.id)
        ).fetchone()[0]
        db.commit()
        return await get_category_by_id(id=id, db=db)
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def update_category(
    id: int, data: schemas.CategoryUpdate, db: Session
) -> schemas.Category:
    try:
        query = db.query(models.Category).filter(models.Category.id == id)
        db_category = query.first()
        if not db_category:
            raise CategoryNotFound()
        db_category.type = data.type
        db_category.name = data.name
        db.commit()
        return await get_category_by_id(id=id, db=db)
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def delete_category(id: int, db: Session):
    try:
        query = db.query(models.Category).filter(models.Category.id == id)
        if not query.first():
            raise CategoryNotFound()
        query.delete()
        db.commit()
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def get_category_name(category_id: int, db: Session) -> str:
    try:
        return db.execute(
            select(models.Category.name).where(models.Category.id == category_id)
        ).fetchone()[0]
    except Exception as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()
