from sqlalchemy import Column, Integer, String, TIMESTAMP
from datetime import datetime

from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column()
    password = Column()
    phone = Column()
    role = Column()
    onblacklist = Column()
    created_at = Column(TIMESTAMP, default=datetime.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "phone": self.phone,
            "role": self.role,
            "onblacklist": self.onblacklist,
            "created_at": self.created_at
            #"password": self.password,
        }
