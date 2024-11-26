from sqlalchemy import insert, or_, select, update
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.exceptions import *
from ..core.config import logger


async def category_in_db(id: int, db: Session) -> bool:
    cnt: int = db.query(models.Category).filter(models.Category.id == id).count()
    if cnt:
        return True
    return False


async def get_db_category(id: int, db: Session) -> models.Category:
    db_category: models.Category = (
        db.query(models.Category).filter(models.Category.id == id).first()
    )
    if not db_category:
        raise CategoryNotFound()
    return db_category


async def get_category_by_id(id: int, db: Session) -> schemas.Category:
    db_category: models.Category = await get_db_category(id=id, db=db)
    return schemas.Category(**db_category.to_dict())


async def get_all_categories(db: Session, type: str = None) -> list[schemas.Category]:
    results = [
        schemas.Category(**db_category.to_dict())
        for db_category in db.query(models.Category)
        .filter(or_(type is None, models.Category.type == type))
        .all()
    ]
    return results


async def create_category(
    data: schemas.CategoryCreate, db: Session
) -> schemas.Category:
    id: int = db.execute(
        insert(models.Category)
        .values(**data.model_dump())
        .returning(models.Category.id)
    ).fetchone()[0]
    db.commit()
    return await get_category_by_id(id=id, db=db)


async def update_category(
    id: int, data: schemas.CategoryUpdate, db: Session
) -> schemas.Category:
    db.execute(
        update(models.Category)
        .where(models.Category.id == id)
        .values(**data.model_dump())
    )
    db.commit()
    return await get_category_by_id(id=id, db=db)


async def delete_category(id: int, db: Session) -> None:
    query = db.query(models.Category).filter(models.Category.id == id)
    if not query.first():
        raise CategoryNotFound()
    query.delete()
    db.commit()


async def get_category_name(id: int, db: Session) -> str:
    category: schemas.Category = await get_category_by_id(id=id, db=db)
    return category.name
