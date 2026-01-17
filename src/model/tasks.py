from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
    """Базовая модель для работы с задачами."""
    name: str = Field(
        title="Название",
        max_length=80
    )
    description: str | None = Field(
        default=None,
        title="Описание",
        max_length=300
    )
    deadline: datetime | None = Field(
        default=None,
        title="Срок выполнения"
    )

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo:
            now = datetime.now(timezone.utc)
            if value.tzinfo is False:
                raise ValueError(
                    "Введите дату в формате utc: 2026-12-31T02:06:16.662Z")
            if value <= now:
                raise ValueError(
                    'deadline не может быть меньше текущего времени')
        return value


class TaskCreate(TaskBase):
    """Модель для создания задачи."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Изучить FastAPI",
                    "description": "1. Изучить Path, Query-параметры",
                    "deadline": "2026-12-31T15:53:00+05:00"
                }
            ]
        }
    }


class TaskResponse(TaskBase):
    """Модель для возврата данных задачи."""
    id: int
    status: bool = Field(
        default=True,
        title="Статус задачи"
    )
    created_at: datetime = Field(
        title="Время создания"
    )


class TaskUpdate(BaseModel):
    """
    Модель для обновления существующей задачи.
    Все поля опциональны - обновляются только переданные значения.
    """
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    status: bool | None = None
