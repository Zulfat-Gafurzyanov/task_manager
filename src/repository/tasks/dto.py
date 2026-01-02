from datetime import datetime

from pydantic import BaseModel


class TaskCreateDTO(BaseModel):
    """DTO для создания задачи."""
    name: str
    description: str | None
    deadline: datetime | None


class TaskDTO(BaseModel):
    """DTO для возвращения задачи."""
    id: int
    name: str
    description: str | None
    deadline: datetime | None
    status: bool
    created_at: datetime


class TaskUpdateDTO(BaseModel):
    """DTO для изменения задачи."""
    name: str
    description: str | None
    deadline: datetime | None
    status: bool
