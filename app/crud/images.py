from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session

from ..core.exceptions import *
from .. import schemas, models
from ..core.config import logger


async def get_project_images(id: int, db: Session) -> list[schemas.Image]:
    return [
        schemas.Image(**image.to_dict())
        for image in db.query(models.Image)
        .filter(models.Image.usage == "PROJECT", models.Image.master_id == id)
        .all()
    ]


async def add_project_images(id: int, images: list[schemas.Image], db: Session) -> None:
    for image in images:
        image_dict: dict = image.model_dump(exclude_unset=True)
        image_dict["master_id"] = id
        image_dict["usage"] = "PROJECT"
        db.add(models.Image(**image_dict))
    db.commit()


async def delete_project_images(id: int, db: Session) -> None:
    db.execute(
        delete(models.Image).where(
            models.Image.usage == "PROJECT", models.Image.master_id == id
        )
    )
    db.commit()


async def get_product_images(id: int, db: Session) -> list[schemas.Image]:
    return [
        schemas.Image(**image.to_dict())
        for image in db.query(models.Image)
        .filter(models.Image.usage == "PRODUCT", models.Image.master_id == id)
        .all()
    ]

async def add_product_images(id: int, images: list[schemas.Image], db: Session) -> None:
    for image in images:
        image_dict: dict = image.model_dump(exclude_unset=True)
        image_dict["master_id"] = id
        image_dict["usage"] = "PRODUCT"
        db.add(models.Image(**image_dict))
    db.commit()


async def delete_product_images(id: int, db: Session) -> None:
    db.execute(
        delete(models.Image).where(
            models.Image.usage == "PRODUCT", models.Image.master_id == id
        )
    )
    db.commit()
