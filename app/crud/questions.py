from sqlalchemy import insert, or_, select, update
from sqlalchemy.orm import Session


from .. import models, schemas, utils
from ..core.exceptions import *
from ..core.config import logger


async def get_db_question(id: int, db: Session) -> models.Question:
    db_question = db.query(models.Question).filter(models.Question.id == id).first()
    if not db_question:
        raise QuestionNotFound()
    return db_question


async def get_question_by_id(id: int, db: Session) -> schemas.Question:
    db_question: models.Question = await get_db_question(id=id, db=db)
    return schemas.Question(**db_question.to_dict())


async def get_all_questions(
    db: Session, answered: bool = None, page: int = 1, limit: int = 10
) -> list[schemas.Question]:
    return [
        schemas.Question(**db_question.to_dict())
        for db_question in db.query(models.Question)
        .filter(or_(answered is None, models.Question.answered == answered))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    ]


async def create_question(
    data: schemas.CreateQuestion, db: Session
) -> schemas.Question:
    data_dict: dict = data.model_dump()
    data_dict["answered"] = False
    id: int = db.execute(
        insert(models.Question).values(**data_dict).returning(models.Question.id)
    ).fetchone()[0]
    db.commit()
    return await get_question_by_id(id=id, db=db)


async def answer_question(
    data: schemas.AnswerQuestion, db: Session
):
    question: schemas.Question = await get_question_by_id(id=data.id, db=db)
    await utils.send_email(
        to=[question.email],
        subject="Jana Dubai - Reply on your question",
        body=data.message,
    )
    db.execute(
        update(models.Question)
        .where(models.Question.id == data.id)
        .values(answered=True)
    )
    db.commit()
    return {"message": "The answer has been sent successfully"}


async def delete_question(id: int, db: Session) -> None:
    query = db.query(models.Question).filter(models.Question.id == id)
    if not query.first():
        raise QuestionNotFound()
    query.delete()
    db.commit()
