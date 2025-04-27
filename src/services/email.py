from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import SecretStr

from src.services.auth import create_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email(email: str, username: str, host: str):
    """
    Send a verification email

    Args:
        email (str): email address
        username (str): username
        host (str): host address

    Returns:
        None
    """

    try:
        token = create_token(payload={"sub": email})
        message = MessageSchema(
            subject="Verify your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verification_email.html")
    except ConnectionErrors as e:
        print(e)


async def send_reset_email(email: str, token: str, host: str):
    """
    Send a resent password email

    Args:
        email (str): email address
        token (str): token
        host (str): host address

    Returns:
        None
    """
    try:
        token = create_token(payload={"sub": email})
        message = MessageSchema(
            subject="Reset Password request",
            recipients=[email],
            template_body={
                "host": host,
                "token": token,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_email.html")
    except ConnectionErrors as e:
        print(e)
