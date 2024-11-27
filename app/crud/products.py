from sqlalchemy import and_, insert, or_, update, delete, select, func
from sqlalchemy.orm import Session

from .images import add_product_images, delete_product_images, get_product_images
from .categories import get_category_name
from .. import schemas, models, utils
from ..core.exceptions import *
from ..core.config import logger


async def get_db_product(id: int, db: Session) -> models.Product:
    db_product: models.Product = (
        db.query(models.Product).filter(models.Product.id == id).first()
    )
    if not db_product:
        raise ProductNotFound()
    return db_product


async def get_product_by_id(id: int, db: Session) -> schemas.Product:
    db_product: models.Product = await get_db_product(id=id, db=db)
    category_name: str = await get_category_name(id=db_product.category_id, db=db)
    product_dict: dict = db_product.to_dict()
    product_dict["category_name"] = category_name
    product: schemas.Product = schemas.Product(**product_dict)
    product.images = await get_product_images(id=id, db=db)
    return product


async def get_all_products(
    db: Session, category_id: int = None, page: int = 1, limit: int = 10
) -> list[schemas.Product]:
    return [
        await get_product_by_id(id=product.id, db=db)
        for product in db.query(models.Product)
        .filter(or_(category_id is None, models.Product.category_id == category_id))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    ]


async def search_products(name: str, category_id: int, db: Session):
    return [
        await get_product_by_id(id=product.id, db=db)
        for product in db.query(models.Product)
        .filter(
            and_(
                func.lower(models.Product.name).contains(name.lower()),
                or_(category_id is None, models.Product.category_id == category_id),
            )
        )
        .all()
    ]


async def create_product(data: schemas.ProductCreate, db: Session) -> schemas.Product:
    id: int = db.execute(
        insert(models.Product)
        .values(
            name=data.name,
            category_id=data.category_id,
            description=data.description,
        )
        .returning(models.Product.id)
    ).fetchone()[0]
    await add_product_images(id=id, db=db, images=data.images)
    db.commit()
    return await get_product_by_id(id=id, db=db)


async def update_product(
    id: int, data: schemas.ProductUpdate, db: Session
) -> schemas.Product:
    db.execute(
        update(models.Product)
        .values(
            data.model_dump(exclude_unset=True, exclude_none=True, exclude={"images"})
        )
        .where(models.Product.id == id)
    )
    if "images" in data.model_dump(exclude_unset=True, exclude_none=True):
        await delete_product_images(id=id, db=db)
        await add_product_images(id=id, images=data.images, db=db)
    db.commit()
    return await get_product_by_id(id=id, db=db)


async def delete_product(id: int, db: Session) -> None:
    db.execute(delete(models.Product).where(models.Product.id == id))
    await delete_product_images(id=id, db=db)
    db.commit()
