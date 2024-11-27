from fastapi import APIRouter, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, utils
from .. import crud
from ..core.dependencies import *

router = APIRouter(prefix="/mail")


@router.post(
    path="/send-email/", status_code=status.HTTP_200_OK, tags=["Email"],
)
async def send_email(email: schemas.Email):
    await utils.send_email(to=[email.to], subject=email.subject, body=email.body)
    return {"message": "email has been sent successfully"}