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

    # ???????????????????????????????????
    # Когда использовать model_validator?
    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: datetime | None) -> datetime | None:
        if value is not None and value <= datetime.now(timezone.utc):
            raise ValueError(
                '"Срок выполнения" не может быть меньше текущего времени')
        return value


class TaskCreate(TaskBase):
    pass

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


class TaskUpdate(TaskBase):
    # Подумать над частичной заменой!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pass


class TaskResponse(TaskBase):
    id: int
    status: bool = Field(
        default=False,
        title="Статус задачи"
    )
    created_at: datetime = Field(
        title="Время создания"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "status": False,
                    "created_at": "2025-12-22T15:53:00+05:00",
                    "name": "Изучить FastAPI",
                    "description": "1. Изучить Path, Query-параметры",
                    "deadline": "2030-09-17T12:34:00+05:00"
                }
            ]
        }
    }
