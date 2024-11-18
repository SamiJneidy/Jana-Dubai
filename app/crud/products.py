from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session

from .images import add_product_images, delete_product_images, get_product_images
from .categories import get_category_name
from .. import schemas, models, utils
from ..core.exceptions import *


def get_db_product(product_id: int, db: Session) -> models.Product:
    try:
        product = (
            db.query(models.Product).filter(models.Product.id == product_id).first()
        )
        if not product:
            raise ProductNotFound()
        return product
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_product_by_id(product_id: int, db: Session) -> schemas.Product:
    try:
        db_product: models.Product = get_db_product(product_id=product_id, db=db)
        category_name: str = get_category_name(
            category_id=db_product.category_id, db=db
        )
        product_dict: dict = db_product.to_dict()
        product_dict["category_name"] = category_name
        product: schemas.Product = schemas.Product(**product_dict)
        product.images = get_product_images(product_id=product_id, db=db)
        return product
    except DatabaseError as e:
        print(e)
        raise e


def get_all_products(
    db: Session, categoryId: int = None, page: int = 1, limit: int = 10
) -> list[schemas.Product]:
    try:
        products = [
            get_product_by_id(product.id, db=db)
            for product in db.query(models.Product)
            .filter(or_(categoryId is None, models.Product.category_id == categoryId))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        ]
        return products
    except DatabaseError as e:
        print(e)
        raise e


def create_product(data: schemas.ProductCreate, db: Session) -> schemas.Product:
    try:
        id = db.execute(
            insert(models.Product)
            .values(
                name=data.name,
                category_id=data.category_id,
                description=data.description,
            )
            .returning(models.Product.id)
        ).fetchone()[0]
        add_product_images(product_id=id, db=db, images=data.images)
        db.commit()
        return get_product_by_id(product_id=id, db=db)
    except Exception as e:
        print(e)
        raise e


def update_product(
    id: int, data: schemas.ProductUpdate, db: Session
) -> schemas.Product:
    try:
        product: schemas.Product = get_product_by_id(product_id=id, db=db)
        db.execute(
            update(models.Product)
            .values(
                data.model_dump(
                    exclude_unset=True, exclude_none=True, exclude={"images"}
                )
            )
            .where(models.Product.id == id)
        )
        if "images" in data.model_dump(exclude_unset=True, exclude_none=True):
            delete_product_images(product_id=id, db=db)
            add_product_images(product_id=id, images=data.images, db=db)
        db.commit()
        return get_product_by_id(product_id=id, db=db)
    except DatabaseError as e:
        print(e)
        raise e


def delete_product(id: int, db: Session):
    try:
        product = get_product_by_id(product_id=id, db=db)
        db.execute(delete(models.Product).where(models.Product.id == id))
        delete_product_images(product_id=id, db=db)
        db.commit()
    except Exception as e:
        print(e)
        raise e
