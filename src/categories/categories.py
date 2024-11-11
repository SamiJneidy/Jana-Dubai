from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .. import users, auth, exceptions
from .. database import get_db

router = APIRouter(prefix="/categories")

@router.get("/get-categories/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Category)
def get_category_by_id(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    result = db.query(models.Category).filter(models.Category.id == id).first()
    if(not result):
        raise exceptions.ResourceNotFound
    return result

@router.get("/get-categories/", status_code=status.HTTP_200_OK, response_model=List[schemas.Category])
def get_all_categories(type: str = None, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    result = db.query(models.Category).filter(or_(type is None, models.Category.type==type)).all()
    return result

@router.post("/create-category", status_code=status.HTTP_200_OK, response_model=schemas.Category)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    new_category = models.Category(**dict(data))
    db.add(new_category)
    db.commit()
    return new_category

@router.put("/update-category/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Category)
def update_category(id: int, data: schemas.CategoryUpdate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    query = db.query(models.Category).filter(models.Category.id == id)
    db_category = query.first()
    if(not db_category):
        raise exceptions.ResourceNotFound
    db_category.type = data.type
    db_category.name = data.name
    db.commit()
    return query.first()

@router.delete("/delete-category/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    query = db.query(models.Category).filter(models.Category.id == id)
    if(not query.first()):
        raise exceptions.ResourceNotFound
    query.delete()
    db.commit()
