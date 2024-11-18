from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, BOOLEAN
from datetime import datetime

from ..core.database import Base


class Question(Base):
    __tablename__ = "QUESTIONS"
    id = Column(name="id", type_=Integer, primary_key=True)
    email = Column(name="email", type_=String, nullable=False)
    name = Column(name="name", type_=String, nullable=True)
    phone = Column(name="phone", type_=String, nullable=True)
    company = Column(name="company", type_=String, nullable=True)
    message = Column(name="message", type_=String, nullable=False)
    answered = Column(name="answered", type_=BOOLEAN, nullable=True)
    created_at = Column(
        name="created_at", type_=TIMESTAMP(timezone=True), default=datetime.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "company": self.company,
            "message": self.message,
            "answered": self.answered,
            "created_at": self.created_at,
        }
