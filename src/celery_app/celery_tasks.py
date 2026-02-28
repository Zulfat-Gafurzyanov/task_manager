import asyncio
import asyncpg
import logging
import os
import smtplib

from dotenv import load_dotenv

from src.celery_app.smtp_email_backend import SmtpEmailBackend
from src.celery_app.app import app
from src.core.encryption import Encryption

load_dotenv()
logger = logging.getLogger(__name__)


def _get_email_backend() -> SmtpEmailBackend:
    return SmtpEmailBackend(
        smtp_server=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", 1025)),
        from_email=str(os.getenv("FROM_EMAIL")),
        use_tls=os.getenv("USE_TLS", "false").lower() == "true",
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
    )


@app.task(
    queue="emails.welcome",
    autoretry_for=(smtplib.SMTPException,),
    max_retries=3,
    retry_backoff=True
)
def send_welcome_email(username: str, email: str):
    """
    Отправляет на почту приветственное письмо
    после регистрации пользователя.
    """
    try:
        logger.info("Отправляю письмо пользователю: %s", username)
        email_backend = _get_email_backend()

        email_backend.send_email(
            recipient=email,
            subject="Добро пожаловать!",
            body=f"Привет, {username}! Ты успешно зарегистрировался."
        )
        logger.info("Письмо успешно отправлено!")
    except smtplib.SMTPException as e:
        logger.warning("Ошибка при отправке письма: %s", e)


async def _fetch_users():
    conn = await asyncpg.connect(
        os.environ["DATABASE_URL"].replace("postgresql+asyncpg", "postgresql")
    )
    try:
        rows = await conn.fetch('SELECT username, email FROM "user"')
        return [
            {
                "username": row["username"],
                "email": await Encryption.decrypt_value(row["email"])
            }
            for row in rows
        ]
    finally:
        await conn.close()


@app.task(queue="emails.scheduled")
def send_planned_email():
    """
    Отправляет всем пользователям на почту письмо в запланированное время.
    """
    try:
        users = asyncio.run(_fetch_users())

        logger.info("Отправляю письмо %d пользователям", len(users))
        email_backend = _get_email_backend()
        for user in users:
            email_backend.send_email(
                recipient=user["email"],
                subject="Запланированная рассылка",
                body=f"Привет, {user['username']}!"
            )
        logger.info("Рассылка завершена успешно")
    except smtplib.SMTPException as e:
        logger.warning("Ошибка при отправке письма: %s", e)
