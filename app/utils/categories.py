from sqlalchemy import select
from sqlalchemy.orm import Session

from ..import models

def get_category_name(category_id: int, db: Session) -> str:
    return db.execute(
        select(models.Category.name).
        where(models.Category.id == category_id)
    ).fetchone()[0]