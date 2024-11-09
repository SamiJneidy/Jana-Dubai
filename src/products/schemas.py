from typing import Optional
from pydantic import BaseModel

class Image(BaseModel):
    content: bytes
    mime_type: str

class Product(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: str
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []

class ProductCreate(BaseModel):
    name: str
    category_id: int
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []
    