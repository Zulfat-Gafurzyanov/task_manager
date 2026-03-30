import logging

from notification.src.ws.manager import manager

logger = logging.getLogger(__name__)


async def handle_task_created(data: dict):
    task_id = data["task_id"]
    user_id = data["user_id"]
    logger.info(
        "[NOTIFY] Задача #%s создана пользователем #%s", task_id, user_id)
    await manager.send_to_user(user_id, {
        "event": "task_created",
        "task_id": task_id,
    })


async def handle_task_updated(data: dict):
    task_id = data["task_id"]
    user_id = data["user_id"]
    updated_fields = data.get("updated_fields", {})
    logger.info(
        "[NOTIFY] Задача #%s обновлена пользователем #%s. Поля: %s",
        task_id, user_id, list(updated_fields.keys()),
    )
    await manager.send_to_user(user_id, {
        "event": "task_updated",
        "task_id": task_id,
        "updated_fields": list(updated_fields.keys()),
    })


async def handle_status_updated(data: dict):
    task_id = data["task_id"]
    user_id = data["user_id"]
    status_id = data["status_id"]
    logger.info(
        "[NOTIFY] Статус задачи #%s изменён на #%s пользователем #%s",
        task_id, status_id, user_id,
    )
    await manager.send_to_user(user_id, {
        "event": "task_status_updated",
        "task_id": task_id,
        "status_id": status_id,
    })


async def handle_task_deleted(data: dict):
    task_id = data["task_id"]
    user_id = data["user_id"]
    logger.info(
        "[NOTIFY] Задача #%s удалена пользователем #%s", task_id, user_id)
    await manager.send_to_user(user_id, {
        "event": "task_deleted",
        "task_id": task_id,
    })


HANDLERS = {
    "task:task_created": handle_task_created,
    "task:task_updated": handle_task_updated,
    "task:task_statuses_updated": handle_status_updated,
    "task:task_deleted": handle_task_deleted,
}
