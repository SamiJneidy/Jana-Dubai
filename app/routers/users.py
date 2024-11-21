from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix='/users')

@router.get(path="/get-users/{id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.User)
async def get_user_by_id(id: int, 
             db: Session = Depends(get_db), 
             current_admin: schemas.User = Depends(get_current_admin)):
    return await crud.get_user_by_id(id=id, db=db)

@router.get(path="/get-users/", 
            status_code=status.HTTP_200_OK, 
            response_model=List[schemas.User])
async def get_all_users(db: Session = Depends(get_db), 
                  current_admin: schemas.User = Depends(get_current_admin)):
    return await crud.get_all_users(db=db)
