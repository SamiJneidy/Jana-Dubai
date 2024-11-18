from typing import Optional
from pydantic import BaseModel

from .images import Image


class Project(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: str
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []


class ProjectCreate(BaseModel):
    name: str
    category_id: int
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[list[str]] = []
    images: Optional[list[Image]] = []
