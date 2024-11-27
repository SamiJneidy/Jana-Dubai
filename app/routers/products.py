from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix="/products")


@router.get(
    path="/get-products/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Product,
    tags=["Products"],
)
async def get_single_product(id: int, db: Session = Depends(get_db)):
    return await crud.get_product_by_id(product_id=id, db=db)


@router.get(
    path="/get-products/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Product],
    tags=["Products"],
)
async def get_all_products(
    categoryId: int = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return await crud.get_all_products(
        db=db, category_id=categoryId, page=page, limit=limit
    )


@router.get(
    path="/search-products/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Product],
    tags=["Products"],
)
async def search_products(
    name: str,
    categoryId: int = None,
    db: Session = Depends(get_db),
):
    return await crud.search_products(name=name, category_id=categoryId, db=db)


@router.post(
    path="/create-product/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Product,
    tags=["Products"],
)
async def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return await crud.create_product(data=data, db=db)


@router.put(
    path="/update-product/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Product,
    tags=["Products"],
)
async def update_product(
    id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return await crud.update_product(id=id, data=data, db=db)


@router.delete(
    path="/delete-product/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
)
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    await crud.delete_product(id=id, db=db)
