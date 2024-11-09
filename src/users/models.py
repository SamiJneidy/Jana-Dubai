from sqlalchemy import Column, Integer, String, TIMESTAMP
from ..database import Base
from datetime import datetime
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column()
    password = Column()
    phone = Column()
    role = Column()
    onblacklist = Column()
    created_at = Column(TIMESTAMP, default=datetime.now())
