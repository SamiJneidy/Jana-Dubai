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
    tags=["Questions"],
)
async def get_question_by_id(id: int, db: Session = Depends(get_db)):
    return await crud.get_question_by_id(id=id, db=db)


@router.get(
    path="/get-questions/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Question],
    tags=["Questions"],
)
async def get_all_questions(
    answered: bool = None, page: int = 1, limit: int = 10, db: Session = Depends(get_db)
):
    return await crud.get_all_questions(
        answered=answered, page=page, limit=limit, db=db
    )


@router.post(
    path="/create-question/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Question,
    tags=["Questions"],
)
async def create_question(data: schemas.CreateQuestion, db: Session = Depends(get_db)):
    return await crud.create_question(data=data, db=db)


@router.post(
    path="/answer-question/",
    status_code=status.HTTP_200_OK,
    tags=["Questions"],
)
async def create_question(
    data: schemas.AnswerQuestion,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return await crud.answer_question(data=data, db=db)


@router.delete(
    path="/delete-question/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Questions"],
)
async def delete_question(
    id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)
):
    await crud.delete_question(id=id, db=db)
