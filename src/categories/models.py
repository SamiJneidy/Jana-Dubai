from ..database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from datetime import datetime
class Category(Base):
    __tablename__ = "CATEGORIES"
    id = Column(name="Id", type_=Integer, primary_key=True)
    type = Column(name="Type", type_=String, nullable=False)
    name = Column(name="Name", type_=String, nullable=False)
    created_at = Column(name="CreatedAt", type_=TIMESTAMP(timezone=True), default=datetime.now())
    created_by = Column(name="CreatedBy", type_=Integer)