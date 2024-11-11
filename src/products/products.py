from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .. import users, auth, exceptions, categories, images
from ..database import get_db

router = APIRouter(prefix="/products")
def get_product(id: int, db: Session) -> schemas.Product:
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if(not product):
        raise exceptions.ResourceNotFound
    category_name = categories.utils.get_category_name(category_id=product.category_id, db=db)
    product = product.to_dict()
    product["category_name"] = category_name
    product = schemas.Product(**product)
    product_images = [
        schemas.Image(**image.to_dict()) for image in db.query(images.models.Image).
        filter(images.models.Image.usage == "PRODUCT", images.models.Image.master_id == id).
        all()
    ]
    product.images = product_images
    return product

@router.get("/get-products/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Product)
def get_single_product(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    return get_product(id=id, db=db)

@router.get("/get-products/", status_code=status.HTTP_200_OK, response_model=List[schemas.Product])
def get_all_products(categoryId: int = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    products = [
        get_product(product.id, db=db) for product in db.query(models.Product).
        filter(or_(categoryId is None or models.Product.category_id == categoryId)).
        offset((page-1) * limit). 
        limit(limit)
        .all()
    ]
    return products

@router.post("/create-product", status_code=status.HTTP_200_OK, response_model=schemas.Product)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    id = db.execute(
        insert(models.Product).
        values(name=data.name, category_id=data.category_id, description=data.description).
        returning(models.Product.id)
    ).fetchone()[0]
    for image in data.images:
        image_dict = image.model_dump(exclude_unset=True)
        image_dict["master_id"] = id
        image_dict["usage"] = "PRODUCT"
        db.add(images.models.Image(**image_dict))
    db.commit()
    return get_product(id=id, db=db)

@router.put("/update-product/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Product)
def update_product(id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if(not product):
        raise exceptions.ResourceNotFound
    db.execute(
        update(models.Product).
        values(data.model_dump(exclude_unset=True, exclude_none=True, exclude={"images"})).
        where(models.Product.id == id)
    )
    if("images" in data.model_dump(exclude_unset=True, exclude_none=True)):

        db.execute(
            delete(images.models.Image).
            where(images.models.Image.usage == "PRODUCT", images.models.Image.master_id == id)
        )
        for image in data.images:
            image_dict = image.model_dump(exclude_unset=True, exclude_none=True)
            image_dict["master_id"] = id
            image_dict["usage"] = "PRODUCT"
            db.add(images.models.Image(**image_dict))
    db.commit()
    return get_product(id=id, db=db)

@router.delete("/delete-product/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    
    product = db.execute(
        select(models.Product).
        where(models.Product.id == id)
    ).fetchone()

    if(not product):
        raise exceptions.ResourceNotFound
    
    db.execute(
        delete(models.Product).
        where(models.Product.id == id)
    )
    db.execute(
        delete(images.models.Image).
        where(images.models.Image.usage == "PRODUCT", images.models.Image.master_id == id)
    )
    db.commit()
