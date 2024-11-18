from fastapi import APIRouter, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..core.dependencies import *

router = APIRouter(prefix="/auth")


@router.post(
    path="/signup", status_code=status.HTTP_200_OK, response_model=schemas.User
)
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.signup(data=data, db=db)


@router.post(
    path="/login", status_code=status.HTTP_200_OK, response_model=schemas.AccessToken
)
def login(user: schemas.Login, db: Session = Depends(get_db)):
    token: schemas.AccessToken = crud.login(user=user, db=db)
    return token


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: schemas.User = Depends(get_current_user),
    token: str = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    crud.logout(token=token, db=db)

@router.get(path='/get-current-user', 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.User)
def get_current_user_controller(db: Session = Depends(get_db), 
                     current_user: schemas.User = Depends(get_current_user)):
    return current_user

# @router.post(path='/forgot-password',
#              status_code=status.HTTP_200_OK)
# def get_password_reset_link(user: schemas.ForgotPassword,
#                             db: Session = Depends(get_db)):
#     db_user = db.query(users.models.User).filter(users.models.User.username==user.email).first()
#     if(not db_user):
#         raise exceptions.ResourceNotFound(detail="Username not found")
#     payload = schemas.TokenPayload(username=user.email).model_dump()
#     token = utils.create_access_token(to_encode=payload, expire_minutes=settings.password_reset_token_expire_minutes, usage="password_reset", db=db)
#     reset_link = f'http://localhost:8000/password-reset/?token={token.token}'
#     mail.send_email(
#                 to=[user.email],
#                 subject="Jana Dubai - Password Reset Request",
#                 body=f"Follow the link to change your password: {reset_link} . If you think you got this message by mistake, just ignore it.",
#     )
#     return {"message": f"An email has been sent to {user.email}. Check you inbox or spam folder to reset your password.",
#             "token": token.token}

# @router.post('/reset-password/', status_code=status.HTTP_200_OK)
# def change_password(data: schemas.ResetPassword, token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         if(not utils.token_in_valid_jwts(token=token, usages="password_reset")):
#             raise exceptions.InvalidToken
#         username = utils.get_user_from_token(token=data.token, db=db).username
#         db_user = db.query(users.models.User).filter(users.models.User.username == username).first()
#         if(not db_user):
#             raise exceptions.ResourceNotFound(detail="Username not found")
#         db_user.password = utils.hash_password(data.password)
#         db.commit()
#         return {"message": "Password has been changes successfuly"}
#     except jwt.InvalidTokenError:
#         raise exceptions.InvalidToken
