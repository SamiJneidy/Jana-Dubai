from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix="/projects")


@router.get(
    path="/get-projects/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Project,
    tags=["Projects"],
)
async def get_single_project(id: int, db: Session = Depends(get_db)):
    return await crud.get_project_by_id(id=id, db=db)


@router.get(
    path="/get-projects/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Project],
    tags=["Projects"],
)
async def get_all_projects(
    categoryId: int = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return await crud.get_all_projects(
        db=db, category_id=categoryId, page=page, limit=limit
    )


@router.post(
    path="/create-project/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Project,
    tags=["Projects"],
)
async def create_project(
    data: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return await crud.create_project(data=data, db=db)


@router.put(
    path="/update-project/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Project,
    tags=["Projects"],
)
async def update_project(
    id: int,
    data: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    return await crud.update_project(id=id, data=data, db=db)


@router.delete(
    path="/delete-project/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Projects"],
)
async def delete_project(
    id: int,
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(get_current_admin),
):
    await crud.delete_project(id=id, db=db)
