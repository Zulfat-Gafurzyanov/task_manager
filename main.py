from fastapi import FastAPI
from pydantic import BaseModel


class Task(BaseModel):
    """Модель данных для задач."""

    name: str
    description: str | None = None


app = FastAPI()


@app.post("/tasks/")
async def create_task(task: Task):
    return task
