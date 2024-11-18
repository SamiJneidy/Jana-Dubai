from pydantic import BaseModel

type = ["products", "projects"]
class Category(BaseModel):
    id: int
    type: str
    name: str

class CategoryCreate(BaseModel):
    type: str
    name: str

class CategoryUpdate(BaseModel):
    type: str
    name: str