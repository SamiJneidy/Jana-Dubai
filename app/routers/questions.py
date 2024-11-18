from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix="/questions")


@router.get(
    path="/get-questions/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Question,
)
def get_question_by_id(id: int, db: Session = Depends(get_db)):
    return crud.get_question_by_id(id=id, db=db)


@router.get(
    path="/get-questions/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Question],
)
def get_all_questions(db: Session = Depends(get_db)):
    return crud.get_all_questions(db=db)


@router.post(
    path="/create-question",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Question,
)
def create_question(data: schemas.CreateQuestion, db: Session = Depends(get_db)):
    return crud.create_question(data=data, db=db)


# @router.put(
#     path="/update-question/{id}",
#     status_code=status.HTTP_200_OK,
#     response_model=schemas.Question,
# )
# def update_question(
#     id: int,
#     data: schemas.QuestionUpdate,
#     db: Session = Depends(get_db),
#     current_admin: schemas.User = Depends(get_current_admin),
# ):
#     return crud.update_question(id=id, data=data, db=db)


# @router.delete(path="/delete-question/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_question(
#     id: int,
#     db: Session = Depends(get_db),
#     current_admin: schemas.User = Depends(get_current_admin),
# ):
#     crud.delete_question(id=id, db=db)
