from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session

from ..core.exceptions import *
from .. import schemas, models


def get_project_images(project_id: int, db: Session) -> list[schemas.Image]:
    try:
        project_images = [
            schemas.Image(**image.to_dict())
            for image in db.query(models.Image)
            .filter(
                models.Image.usage == "PROJECT", models.Image.master_id == project_id
            )
            .all()
        ]
        return project_images
    except Exception as e:
        print(e)
        raise UnexpectedError()


def add_project_images(project_id: int, images: list[schemas.Image], db: Session):
    try:
        for image in images:
            image_dict: dict = image.model_dump(exclude_unset=True)
            image_dict["master_id"] = project_id
            image_dict["usage"] = "PROJECT"
            db.add(models.Image(**image_dict))
        db.commit()
    except Exception as e:
        print(e)
        raise UnexpectedError()


def delete_project_images(project_id: int, db: Session):
    try:
        db.execute(
            delete(models.Image).where(
                models.Image.usage == "PROJECT", models.Image.master_id == project_id
            )
        )
        db.commit()
    except Exception as e:
        print(e)
        raise UnexpectedError()


def get_product_images(product_id: int, db: Session) -> list[schemas.Image]:
    try:
        product_images = [
            schemas.Image(**image.to_dict())
            for image in db.query(models.Image)
            .filter(
                models.Image.usage == "PRODUCT", models.Image.master_id == product_id
            )
            .all()
        ]
        return product_images
    except Exception as e:
        print(e)
        raise UnexpectedError()


def add_product_images(product_id: int, images: list[schemas.Image], db: Session):
    try:
        for image in images:
            image_dict: dict = image.model_dump(exclude_unset=True)
            image_dict["master_id"] = product_id
            image_dict["usage"] = "PRODUCT"
            db.add(models.Image(**image_dict))
        db.commit()
    except Exception as e:
        print(e)
        raise UnexpectedError()


def delete_product_images(product_id: int, db: Session):
    try:
        db.execute(
            delete(models.Image).where(
                models.Image.usage == "PRODUCT", models.Image.master_id == product_id
            )
        )
        db.commit()
    except Exception as e:
        print(e)
        raise UnexpectedError()
