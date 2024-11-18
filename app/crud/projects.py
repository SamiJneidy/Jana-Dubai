from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session
from typing import List

from .images import add_project_images, delete_project_images, get_project_images
from .. import schemas, models, utils
from ..core.exceptions import *


def get_db_project(project_id: int, db: Session) -> models.Project:
    try:
        project = (
            db.query(models.Project).filter(models.Project.id == project_id).first()
        )
        if not project:
            raise ProjectNotFound()
        return project
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_project_by_id(project_id: int, db: Session) -> schemas.Project:
    try:
        db_project: models.Project = get_db_project(project_id=project_id, db=db)
        category_name: str = utils.get_category_name(
            category_id=db_project.category_id, db=db
        )
        project_dict: dict = db_project.to_dict()
        project_dict["category_name"] = category_name
        project: schemas.Project = schemas.Project(**project_dict)
        project.images = get_project_images(project_id=project_id, db=db)
        return project
    except DatabaseError as e:
        print(e)
        raise e


def get_all_projects(
    db: Session, categoryId: int = None, page: int = 1, limit: int = 10
) -> list[schemas.Project]:
    try:
        projects = [
            get_project_by_id(project.id, db=db)
            for project in db.query(models.Project)
            .filter(or_(categoryId is None, models.Project.category_id == categoryId))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        ]
        return projects
    except DatabaseError as e:
        print(e)
        raise e


def create_project(data: schemas.ProjectCreate, db: Session) -> schemas.Project:
    try:
        id = db.execute(
            insert(models.Project)
            .values(
                name=data.name,
                category_id=data.category_id,
                description=data.description,
            )
            .returning(models.Project.id)
        ).fetchone()[0]
        add_project_images(project_id=id, db=db, images=data.images)
        db.commit()
        return get_project_by_id(project_id=id, db=db)
    except Exception as e:
        print(e)
        raise e


def update_project(
    id: int, data: schemas.ProjectUpdate, db: Session
) -> schemas.Project:
    try:
        project: schemas.Project = get_project_by_id(project_id=id, db=db)
        db.execute(
            update(models.Project)
            .values(
                data.model_dump(
                    exclude_unset=True, exclude_none=True, exclude={"images"}
                )
            )
            .where(models.Project.id == id)
        )
        if "images" in data.model_dump(exclude_unset=True, exclude_none=True):
            delete_project_images(project_id=id, db=db)
            add_project_images(project_id=id, images=data.images, db=db)
        db.commit()
        return get_project_by_id(project_id=id, db=db)
    except DatabaseError as e:
        print(e)
        raise e


def delete_project(id: int, db: Session):
    try:
        project = get_project_by_id(project_id=id, db=db)
        db.execute(delete(models.Project).where(models.Project.id == id))
        delete_project_images(project_id=id, db=db)
        db.commit()
    except Exception as e:
        print(e)
        raise e
