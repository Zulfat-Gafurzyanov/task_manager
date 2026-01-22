import datetime

from pydantic import BaseModel, Field


class Status(BaseModel):
    """Модель для статуса."""
    name: str = Field(title="Статус", max_length=64)


class TagCreate(BaseModel):
    """Модель для создания тега."""
    name: str = Field(title="Тег", max_length=64)


class TagResponse(BaseModel):
    """Модель для возврата тега."""
    id: int
    name: str = Field(title="Тег", max_length=64)


class TaskBase(BaseModel):
    """Базовая модель для работы с задачами."""

    name: str = Field(max_length=64)
    description: str | None = Field(
        default=None,
        max_length=264
    )
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None

# TODO: создать валидацию модели по полям deadline end и start.
#       Чтобы end > start.


class TaskCreate(TaskBase):
    """Модель для создания задачи."""
    pass
# TODO: сделать примеры для создания задачи.


class TaskResponse(TaskBase):
    """Модель для возврата данных задачи."""
    id: int


class TaskUpdate(BaseModel):
    """
    Модель для обновления существующей задачи.
    Все поля опциональны - обновляются только переданные значения.
    """
    name: str | None = None
    description: str | None = None
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: list[int] = []
