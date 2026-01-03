from datetime import datetime

from pydantic import BaseModel


# ???
# Здесь валидация полей тоже нужна?
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

    model_config = {"from_attributes": True}  # Для работы с ORM.


class TaskUpdateDTO(BaseModel):
    """DTO для изменения задачи."""
    name: str | None
    description: str | None
    deadline: datetime | None
    status: bool | None
