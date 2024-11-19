from fastapi import APIRouter, Request, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..core.dependencies import *

router = APIRouter(prefix="/auth")


@router.post(
    path="/signup/", status_code=status.HTTP_200_OK, response_model=schemas.User
)
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.signup(data=data, db=db)


@router.post(
    path="/login/", status_code=status.HTTP_200_OK, response_model=schemas.LoginResponse
)
def login(credentials: schemas.Login, db: Session = Depends(get_db)):
    token: schemas.AccessToken = crud.login(credentials=credentials, db=db)
    return token


@router.post(path="/logout/", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: schemas.User = Depends(get_current_user),
    token: str = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    crud.logout(token=token, db=db)

@router.get(path='/get-current-user/', 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.User)
def get_current_user_controller(db: Session = Depends(get_db), 
                     current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.post(path='/forgot-password/',
             status_code=status.HTTP_200_OK)
def get_password_reset_link(user: schemas.ForgotPassword,
                            request: Request,
                            db: Session = Depends(get_db)):
    return crud.get_password_reset_link(user=user, host_url=request.base_url, db=db)

@router.post('/reset-password/', status_code=status.HTTP_200_OK)
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):
    return crud.reset_password(data=data, db=db)
    
