from fastapi import FastAPI
from .users.users import router as users_router
from .auth.oauth2 import router as auth_router
from .categories.categories import router as categories_router
from .products.products import router as products_router
from .projects.projects import router as projects_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(projects_router)
#run server: uvicorn src.main:app --host 26.246.132.2 --port 8000 --reload