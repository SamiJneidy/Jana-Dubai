from sqlalchemy import Column, Integer, String, TIMESTAMP, ARRAY, LargeBinary
from ..database import Base

class Image(Base):
    __tablename__ = "IMAGES"
    id = Column(name="ID", type_=Integer, primary_key=True)
    usage = Column(name="USAGE", type_=String, nullable=False)
    master_id = Column(name="MASTER_ID", type_=Integer, nullable=False)
    content = Column(name="CONTENT", type_=LargeBinary, nullable=False)
    mime_type = Column(name="MIME_TYPE", type_=String, nullable=False)

    def to_dict(self):
        return {"id":self.id, "master_id":self.master_id, "usage":self.usage, "content":self.content, "mime_type":self.mime_type}
