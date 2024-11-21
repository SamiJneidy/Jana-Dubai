from sqlalchemy import insert, or_, select, update
from sqlalchemy.orm import Session


from .. import models, schemas, utils
from ..core.exceptions import *
from ..core.config import logger

async def get_question_by_id(id: int, db: Session) -> schemas.Question:
    try:
        db_question = db.query(models.Question).filter(models.Question.id == id).first()
        if not db_question:
            raise QuestionNotFound()
        question: schemas.Question = schemas.Question(**db_question.to_dict())
        return question
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def get_all_questions(
    db: Session, answered: bool = None, page: int = 1, limit: int = 10
) -> list[schemas.Question]:
    try:
        results = [
            schemas.Question(**db_question.to_dict())
            for db_question in db.query(models.Question)
            .filter(or_(answered is None, models.Question.answered==answered))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        ]
        return results
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def create_question(data: schemas.CreateQuestion, db: Session) -> schemas.Question:
    try:
        data_dict = data.model_dump()
        data_dict["answered"] = False
        id: int = db.execute(
            insert(models.Question).values(**data_dict).returning(models.Question.id)
        ).fetchone()[0]
        db.commit()
        return get_question_by_id(id=id, db=db)
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def answer_question(data: schemas.AnswerQuestion, db: Session) -> schemas.Question:
    try:
        question: schemas.Question = get_question_by_id(id=data.id, db=db)
        utils.send_email(
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
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()


async def delete_question(id: int, db: Session):
    try:
        question = db.query(models.Question).filter(models.Question.id == id)
        if not question.first():
            raise QuestionNotFound()
        question.delete()
        db.commit()
    except DatabaseError as e:
        logger.error(msg=f"An error has occurred: {e}", exc_info=True)
        raise UnexpectedError()