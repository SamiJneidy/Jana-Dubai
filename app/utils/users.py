#To be removed


from sqlalchemy.orm import Session
from sqlalchemy import select, text

from .. import schemas, models
from ..core.database import get_connection

def insert_user(user: schemas.UserCreate):
    cursor = get_connection()
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


