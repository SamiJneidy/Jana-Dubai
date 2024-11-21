import asyncio
from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from ..core.config import settings
from ..core.exceptions import UnexpectedError

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


async def send_email(to: List[EmailStr], subject: str, body: str, subtype: str = "plain"):
    try:
        message = MessageSchema(
            subject=subject, body=body, recipients=to, subtype=subtype
        )
        await fm.send_message(message)
        # asyncio.run(fm.send_message(message))
    except Exception as e:
        print(e)
        raise UnexpectedError()
