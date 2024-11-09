from sqlalchemy import Column, String, TIMESTAMP

from ..database import Base
class ValidJwt(Base):
    __tablename__ = "VALID_JWTS"
    token = Column(name="Token", type_=String, nullable=False, primary_key=True)
    expire_time = Column(name="ExpireTime", type_=TIMESTAMP(timezone=True), nullable=False)
    usage = Column(name="Usage", type_=String, nullable=False, default="login")