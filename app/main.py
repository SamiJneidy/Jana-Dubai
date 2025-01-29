import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from .core.exceptions import ResourceNotFound, register_handlers
from .routers import routers

app = FastAPI()

for router in routers:
    app.include_router(router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_handlers(app=app)

@app.get(path="/", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    return {"message": "Welcome to Jana Dubai, The server is running."}