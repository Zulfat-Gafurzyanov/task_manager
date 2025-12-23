from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Модель данных для задач."""

    id: UUID  # ? По какой логике выбирать UUID или int?
    title: str = Field(
        title='Название',
        max_length=80
    )
    dеscription: str | None = Field(
        default=None,
        title='Описание',
        max_length=300
    )
    complete_before: datetime | None = Field(
        default=None,
        title='Срок выполнения'
        # !Валидация: не может быть меньше created_at
        # !Валидация, не понимаю как обрабатывать дату и время введенное
        # пользователем? Он же НЕ будет вводить в datetime формате
        # или учитывать UTC-зону.
    )
    status: bool = Field(
        default=False,
        title='Статус задачи'
    )
    created_at: datetime = Field(
        title="Время создания"
        # !Валидация: не может быть меньше "now"
    )

    # ? Как правильно создавать примеры в документацию? Как много?
    # ? Все поля брать? В выдаче документации нет порядка полей?
    # ? Нужно использовать поле "field_order"?
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "9e473ae2-d712-4fde-a7ac-cdb342bc89ad",
                    "title": "Изучить FastAPI",
                    "dеscription": "1. Изучить Path, Query-параметры",
                    "complete_before": "2025-12-22T15:53:00+05:00",
                    "completed": False,
                    "created_at": "2025-12-22T15:53:00+05:00"
                }
            ]
        }
    }


class FilterParams(BaseModel):
    """Модель Query-параметров для пагинации и сортировки."""
    model_config = {"extra": "forbid"}  # Запрещаем доп.параметры.

    limit: int = Field(default=20, ge=0)
    offset: int = Field(default=0, ge=0)
    order_by: str = "created_at"


app = FastAPI()

task_db: dict = {}


# ? Нужны ли статус коды? Если они автоматические?
@app.get("/tasks/", status_code=200)
async def get_tasks(filter_query: Annotated[FilterParams, Query()]) -> list:
    """Возвращает список задач."""
    return list(task_db.values())


@app.post("/task/", status_code=201, response_model=Task)
async def create_task(new_task: Task) -> Task:
    """Создает задачу."""
    # ? Какую логику проверки придумать, чтобы повторно не создавалась задача?
    # по названию задачи? Или такая логика не нужна?
    new_task.id = uuid4()
    new_task.created_at = datetime.now(timezone.utc)

    task_db[new_task.id] = new_task
    return new_task


# ? Как в данном случае отдавать статус-код, если задача не найдена?
@app.delete("/task/{task_id}/", status_code=204)
async def delete_task(task_id: UUID):
    if task_id in task_db.keys():
        del task_db[task_id]
        return {"detail": "Задача успешно удалена"}
    else:
        return {"detail": "Задача не найдена"}


@app.put("/task/{task_id}/")
async def update_task():
    pass


@app.patch("/task/{task_id}/")
async def partial_update_task():
    pass
    # сделать TaskUpdate(BaseModel) c некоторыми полями:
    # title, description, status, complete_before.
    # Task(TaskUpdate) расширить до необходимых полей.
