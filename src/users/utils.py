from datetime import datetime
from sqlalchemy import text

from .import schemas
from ..database import get_cursor

def to_dict(rows: list, columns: list):
    result: list = []
    for row in rows:
        dict_row: dict = {}
        for i in range(len(columns)):
            dict_row[columns[i]] = row[i]
        result.append(dict_row)
    return result

def insert_user(user: schemas.UserCreate):
    cursor = get_cursor()
    sql = text(
        """
            insert into users(username, password, phone, role, onblacklist, created_at) 
            values(:username, :password, :phone, :role, :onblacklist, :created_at)
        """
    )
    cursor.execute(sql, {
            "username":user.username, 
            "password":user.password, 
            "phone":user.phone, 
            "role": user.role, 
            "onblacklist":user.onblacklist, 
            "created_at":"now()"
        })
    cursor.commit()
    return

