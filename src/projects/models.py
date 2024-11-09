from sqlalchemy import Column, Integer, String, TIMESTAMP, ARRAY, LargeBinary
from ..database import Base

class Project(Base):
    __tablename__ = "PROJECTS"
    id = Column(name="ID", type_=Integer, primary_key=True)
    name = Column(name="NAME", type_=String, nullable=False)
    category_id = Column(name="CATEGORY_ID", type_=Integer, nullable=False)
    description = Column(name="DESCRIPTION", type_=ARRAY(String))

    def to_dict(self):
        return {"id":self.id, "name":self.name, "category_id":self.category_id, "description":self.description}
        return self.__dict__
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
