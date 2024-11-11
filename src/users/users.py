from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session
from typing import List

from . import schemas, models
from .. import exceptions, auth
from ..database import get_db
# ----------------------------------------------- #
router = APIRouter(prefix='/users')

@router.get("/get-users/{id}", status_code=status.HTTP_200_OK, response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.utils.get_current_admin)):
    result: Query = db.query(models.User).filter(models.User.id == id).first()
    if(not result):
        raise exceptions.ResourceNotFound    
    return result

@router.get("/get-users/", status_code=status.HTTP_200_OK, response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.utils.get_current_admin)):
    return db.query(models.User).all()

@router.post('/signup', status_code=status.HTTP_200_OK, response_model=schemas.User)
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if(db.query(models.User).filter(models.User.username == data.username).first()):
        raise exceptions.ResourceAlreadyInUse
    user = models.User(**dict(data))
    user.password = auth.utils.hash_password(user.password)
    db.add(user)
    db.commit()
    return user
 
@router.put('/update', status_code=status.HTTP_200_OK, response_model=auth.schemas.AccessToken)
def update_user(updated_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.utils.get_current_user), token: str = Depends(auth.utils.get_current_user)):
    query = db.query(models.User).filter(models.User.username == current_user.username)
    db_user = query.first()
    if(auth.utils.verify_password(updated_user.old_password, db_user.password)):
        db_user.username = updated_user.username
        db_user.password = auth.utils.hash_password(updated_user.new_password)
        new_token = auth.utils.create_access_token(to_encode={"username":updated_user.username}, db=db)
        auth.utils.remove_token_from_valid_jwts(token=token, db=db)
        db.commit()
        return new_token
    raise exceptions.InvalidToken