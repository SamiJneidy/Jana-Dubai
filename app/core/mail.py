import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List


conf = ConnectionConfig(
    MAIL_USERNAME = "samihanijneidy@gmail.com",
    MAIL_PASSWORD = "zbiu ojwv frpv utql",
    MAIL_FROM = "samihanijneidy@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

fm = FastMail(conf)

def send_email(to: List[EmailStr], subject: str, body: str, subtype: str = "plain"):
    message = MessageSchema(
        subject=subject,
        body=body,
        recipients=to,
        subtype=subtype
    )
    asyncio.run(fm.send_message(message))