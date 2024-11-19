from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix="/categories")


@router.get(
    path="/get-categories/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Category,
)
def get_category_by_id(id: int, db: Session = Depends(get_db)):
    return crud.get_category_by_id(id=id, db=db)


@router.get(
    path="/get-categories/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Category],
)
def get_all_categories(type: str = None, db: Session = Depends(get_db)):
    return crud.get_all_categories(type=type, db=db)


@router.post(
    path="/create-category/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Category,
)
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return crud.create_category(data=data, db=db)


@router.put(
    path="/update-category/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Category,
)
def update_category(
    id: int,
    data: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return crud.update_category(id=id, data=data, db=db)


@router.delete(path="/delete-category/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    crud.delete_category(id=id, db=db)
