from sqlalchemy import insert, or_
from sqlalchemy.orm import Session


from .. import models, schemas
from ..core.exceptions import *


def get_category_by_id(id: int, db: Session) -> schemas.Category:
    try:
        db_category = db.query(models.Category).filter(models.Category.id == id).first()
        if not db_category:
            raise CategoryNotFound()
        category: schemas.Category = schemas.Category(**db_category.to_dict())
        return category
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_all_categories(db: Session, type: str = None) -> list[schemas.Category]:
    try:
        results = [
            schemas.Category(**db_category.to_dict())
            for db_category in db.query(models.Category)
            .filter(or_(type is None, models.Category.type == type))
            .all()
        ]
        return results
    except Exception as e:
        print(e)
        raise UnexpectedError()


def create_category(data: schemas.CategoryCreate, db: Session) -> schemas.Category:
    try:
        id: int = db.execute(
            insert(models.Category)
            .values(**data.model_dump())
            .returning(models.Category.id)
        ).fetchone()[0]
        db.commit()
        return get_category_by_id(id=id, db=db)
    except Exception as e:
        print(e)
        raise UnexpectedError()


def update_category(
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
        return get_category_by_id(id=id, db=db)
    except Exception as e:
        print(e)
        raise UnexpectedError()


def delete_category(id: int, db: Session):
    try:
        query = db.query(models.Category).filter(models.Category.id == id)
        if not query.first():
            raise CategoryNotFound()
        query.delete()
        db.commit()
    except Exception as e:
        print(e)
        raise UnexpectedError()
