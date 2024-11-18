from sqlalchemy import insert, or_, select
from sqlalchemy.orm import Session


from .. import models, schemas
from ..core.exceptions import *


def get_question_by_id(id: int, db: Session) -> schemas.Question:
    try:
        db_question = db.query(models.Question).filter(models.Question.id == id).first()
        if not db_question:
            raise QuestionNotFound()
        question: schemas.Question = schemas.Question(**db_question.to_dict())
        return question
    except DatabaseError as e:
        print(e)
        raise UnexpectedError()


def get_all_questions(db: Session) -> list[schemas.Question]:
    try:
        results = [
            schemas.Question(**db_question.to_dict())
            for db_question in db.query(models.Question).all()
        ]
        return results
    except Exception as e:
        print(e)
        raise UnexpectedError()


def create_question(data: schemas.CreateQuestion, db: Session) -> schemas.Question:
    try:
        data_dict = data.model_dump()
        data_dict["answered"] = False
        id: int = db.execute(
            insert(models.Question)
            .values(**data_dict)
            .returning(models.Question.id)
        ).fetchone()[0]
        db.commit()
        return get_question_by_id(id=id, db=db)
    except Exception as e:
        print(e)
        raise UnexpectedError()


# def update_question(
#     id: int, data: schemas.QuestionUpdate, db: Session
# ) -> schemas.Question:
#     try:
#         query = db.query(models.Question).filter(models.Question.id == id)
#         db_question = query.first()
#         if not db_question:
#             raise QuestionNotFound()
#         db_question.type = data.type
#         db_question.name = data.name
#         db.commit()
#         return get_question_by_id(id=id, db=db)
#     except Exception as e:
#         print(e)
#         raise UnexpectedError()


# def delete_question(id: int, db: Session):
#     try:
#         query = db.query(models.Question).filter(models.Question.id == id)
#         if not query.first():
#             raise QuestionNotFound()
#         query.delete()
#         db.commit()
#     except Exception as e:
#         print(e)
#         raise UnexpectedError()


# def get_question_name(question_id: int, db: Session) -> str:
#     return db.execute(
#         select(models.Question.name).where(models.Question.id == question_id)
#     ).fetchone()[0]
