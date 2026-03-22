import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exception.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exception):
    """Универсальный обработчик для исключений."""
    logger.warning(
        "AppException: status=%d, path=%s, detail=%s",
        exception.status_code,
        request.url,
        exception.message,
    )
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "detail": exception.message,
            "path": str(request.url)
            }
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация обработчиков исключений."""
    app.add_exception_handler(AppException, app_exception_handler)
