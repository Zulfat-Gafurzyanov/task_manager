from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
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

    # ---???---
    # Когда использовать model_validator?
    # ---???---
    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: datetime | None) -> datetime | None:
        if value is not None and value <= datetime.now(timezone.utc):
            raise ValueError(
                '"Срок выполнения" не может быть меньше текущего времени')
        return value


class TaskCreate(TaskBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Изучить FastAPI",
                    "description": "1. Изучить Path, Query-параметры",
                    "deadline": "2025-12-22T15:53:00+05:00"
                }
            ]
        }
    }


class TaskResponse(TaskBase):
    id: int
    status: bool = Field(
        default=True,
        title="Статус задачи"
    )
    created_at: datetime = Field(
        title="Время создания"
    )


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    status: bool | None = None
