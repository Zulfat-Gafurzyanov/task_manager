import json

from sqlalchemy.exc import IntegrityError

import src.db.connection as db
from src.repository.assigments import AssignmentRepository


async def handle(body: bytes) -> str:
    data = json.loads(body)

    action = data.get("action")
    if action not in ("add", "remove", "list"):
        return json.dumps(
            {"status": "error", "detail": f"Неизвестный action: {action}"})

    task_id = data.get("task_id")
    if task_id is None:
        return json.dumps({"status": "error", "detail": "task_id обязателен"})

    user_id = data.get("user_id")
    if action in ("add", "remove") and user_id is None:
        return json.dumps({"status": "error", "detail": "user_id обязателен"})

    async with db.async_session_factory() as session:
        repo = AssignmentRepository(session)

        if action == "add":
            try:
                await repo.add(task_id, user_id)
                return json.dumps({"status": "ok"})
            except IntegrityError:
                return json.dumps(
                    {"status": "error", "detail": "Пользователь уже назначен"})

        elif action == "remove":
            await repo.remove(task_id, user_id)
            return json.dumps({"status": "ok"})

        else:
            user_ids = await repo.list(task_id)
            return json.dumps({"status": "ok", "data": user_ids})
