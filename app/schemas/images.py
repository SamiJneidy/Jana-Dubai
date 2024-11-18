from pydantic import BaseModel

class Image(BaseModel):
    content: bytes
    mime_type: str