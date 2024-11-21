import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    users_router,
    auth_router,
    categories_router,
    products_router,
    projects_router,
    mail_router,
    questions_router
)

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
app.include_router(mail_router)
app.include_router(questions_router)



@app.get(path="/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to Jana Dubai"}