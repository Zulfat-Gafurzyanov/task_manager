from typing import Annotated

from fastapi import APIRouter

router = APIRouter(prefix="/tasks")


@router.get("")
async def get_tasks(filter_query: Annotated[FilterParams, Query()]) -> list:
    """Возвращает список задач."""
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    return list(task_db.values())  # продумать возврат из БД


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    filter_query: Annotated[FilterParams, Query()]) -> Task:
    """Возвращает список задач."""
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    return list(task_db.values())  # продумать возврат из БД


@app.post("", status_code=201, response_model=Task)
async def create_task(new_task: Task) -> Task:
    """Создает задачу."""
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    # ? Какую логику проверки придумать, чтобы повторно не создавалась задача?
    # по названию задачи? Или такая логика не нужна?
    new_task.id = uuid4()
    new_task.created_at = datetime.now(timezone.utc)

    task_db[new_task.id] = new_task
    return new_task


# ? Как в данном случае отдавать статус-код, если задача не найдена?
@app.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID):
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    if task_id in task_db.keys():
        del task_db[task_id]
        return {"detail": "Задача успешно удалена"}
    else:
        return {"detail": "Задача не найдена"}


@app.put("/{task_id}")
async def update_task():
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    pass


@app.patch("/{task_id}")
async def partial_update_task():
    # ВЫЗОВ сервисного слоя 1 строчка!!!
    pass
    # сделать TaskUpdate(BaseModel) c некоторыми полями:
    # title, description, status, complete_before.
    # Task(TaskUpdate) расширить до необходимых полей.
