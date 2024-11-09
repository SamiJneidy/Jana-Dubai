from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .. import users, auth, exceptions
from ..database import get_db


def get_category_name(category_id: int, db: Session):
    return db.execute(
        select(models.Category.name).
        where(models.Category.id == category_id)
    ).fetchone()[0]