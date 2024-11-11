from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .. import users, auth, exceptions, categories, images
from ..database import get_db

router = APIRouter(prefix="/projects")

def get_project(id: int, db: Session) -> schemas.Project:
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if(not project):
        raise exceptions.ResourceNotFound
    category_name = categories.utils.get_category_name(category_id=project.category_id, db=db)
    project = project.to_dict()
    project["category_name"] = category_name
    project = schemas.Project(**project)
    project_images = [
        schemas.Image(**image.to_dict()) for image in db.query(images.models.Image).
        filter(images.models.Image.usage == "PROJECT", images.models.Image.master_id == id).
        all()
    ]
    project.images = project_images
    return project

@router.get("/get-projects/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Project)
def get_single_project(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    return get_project(id=id, db=db)
@router.get("/get-projects/", status_code=status.HTTP_200_OK, response_model=List[schemas.Project])
def get_all_projects(categoryId: int = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    projects = [
        get_project(project.id, db=db) for project in db.query(models.Project).
        filter(or_(categoryId is None, models.Project.category_id == categoryId)).
        offset((page-1) * limit).
        limit(limit).
        all()
    ]
    return projects

@router.post("/create-project", status_code=status.HTTP_200_OK, response_model=schemas.Project)
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    id = db.execute(
        insert(models.Project).
        values(name=data.name, category_id=data.category_id, description=data.description).
        returning(models.Project.id)
    ).fetchone()[0]
    for image in data.images:
        image_dict = image.model_dump(exclude_unset=True)
        image_dict["master_id"] = id
        image_dict["usage"] = 'PROJECT'
        db.add(images.models.Image(**image_dict))
    db.commit()
    return get_project(id=id, db=db)

@router.put("/update-project/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Project)
def update_project(id: int, data: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if(not project):
        raise exceptions.ResourceNotFound
    db.execute(
        update(models.Project).
        values(data.model_dump(exclude_unset=True, exclude_none=True, exclude={"images"})).
        where(models.Project.id == id)
    )
    if("images" in data.model_dump(exclude_unset=True, exclude_none=True)):
        db.execute(
            delete(images.models.Image).
            where(images.models.Image.usage == "PROJECT", images.models.Image.master_id == id)
        )
        for image in data.images:
            image_dict = image.model_dump(exclude_unset=True, exclude_none=True)
            image_dict["master_id"] = id
            image_dict["usage"] = 'PROJECT'
            db.add(images.models.Image(**image_dict))
    db.commit()
    return get_project(id=id, db=db)

@router.delete("/delete-project/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int, db: Session = Depends(get_db), current_user: users.schemas.User = Depends(auth.utils.get_current_user)):
    
    project = db.execute(
        select(models.Project).
        where(models.Project.id == id)
    ).fetchone()

    if(not project):
        raise exceptions.ResourceNotFound
    
    db.execute(
        delete(models.Project).
        where(models.Project.id == id)
    )
    db.execute(
        delete(images.models.Image).
        where(images.models.Image.usage == "PROJECT", images.models.Image.master_id == id)
    )
    db.commit()
