from sqlalchemy import insert, or_, update, delete, select
from sqlalchemy.orm import Session

from .images import add_project_images, delete_project_images, get_project_images
from .categories import get_category_name
from .. import schemas, models, utils
from ..core.exceptions import *
from ..core.config import logger


async def get_db_project(id: int, db: Session) -> models.Project:
    db_project = db.query(models.Project).filter(models.Project.id == id).first()
    if not db_project:
        raise ProjectNotFound()
    return db_project


async def get_project_by_id(id: int, db: Session) -> schemas.Project:
    db_project: models.Project = await get_db_project(id=id, db=db)
    category_name: str = await get_category_name(id=db_project.category_id, db=db)
    project_dict: dict = db_project.to_dict()
    project_dict["category_name"] = category_name
    project: schemas.Project = schemas.Project(**project_dict)
    project.images = await get_project_images(id=id, db=db)
    return project


async def get_all_projects(
    db: Session, category_id: int = None, page: int = 1, limit: int = 10
) -> list[schemas.Project]:
    return [
        await get_project_by_id(project.id, db=db)
        for project in db.query(models.Project)
        .filter(or_(category_id is None, models.Project.category_id == category_id))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    ]


async def create_project(data: schemas.ProjectCreate, db: Session) -> schemas.Project:
    id: int = db.execute(
        insert(models.Project)
        .values(
            name=data.name,
            category_id=data.category_id,
            description=data.description,
        )
        .returning(models.Project.id)
    ).fetchone()[0]
    await add_project_images(id=id, db=db, images=data.images)
    db.commit()
    return await get_project_by_id(id=id, db=db)


async def update_project(
    id: int, data: schemas.ProjectUpdate, db: Session
) -> schemas.Project:
    db.execute(
        update(models.Project)
        .values(
            data.model_dump(exclude_unset=True, exclude_none=True, exclude={"images"})
        )
        .where(models.Project.id == id)
    )
    if "images" in data.model_dump(exclude_unset=True, exclude_none=True):
        await delete_project_images(id=id, db=db)
        await add_project_images(id=id, images=data.images, db=db)
    db.commit()
    return await get_project_by_id(id=id, db=db)


async def delete_project(id: int, db: Session) -> None:
    db.execute(delete(models.Project).where(models.Project.id == id))
    await delete_project_images(id=id, db=db)
    db.commit()
