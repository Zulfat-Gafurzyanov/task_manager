import os

from dotenv import load_dotenv

from src.celery_app.smtp_email_backend import SmtpEmailBackend
from src.celery_app.app import app

load_dotenv()


@app.task
def send_welcome_email(username: str, email: str):
    """
    Отправляет на почту приветственное письмо
    после регистрации пользователя.
    """

    email_backend = SmtpEmailBackend(
        smtp_server=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", 1025)),
        from_email=str(os.getenv("FROM_EMAIL")),
        use_tls=True,
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
    )

    email_backend.send_email(
        recipient=email,
        subject="Добро пожаловать!",
        body=f"Привет, {username}! Ты успешно зарегистрировался."
    )
