from typing import Literal
from pydantic import BaseModel, Field


class TaskFilterParams(BaseModel):
    """Модель Query-параметров для пагинации и сортировки."""
    model_config = {"extra": "forbid"}  # Запрещаем доп.параметры.

    # Пагинация.
    limit: int = Field(default=100, ge=0)
    offset: int = Field(default=0, ge=0)

    # Сортировка.
    order_by: Literal[
        "id",
        "name",
        "deadline_start",
        "deadline_end",
        "status_id"
    ] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

    # TODO:
    # Фильтры.
