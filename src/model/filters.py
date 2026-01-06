from pydantic import BaseModel, Field


# ???
# в каком файле должна быть эта модель?
class FilterParams(BaseModel):
    """Модель Query-параметров для пагинации и сортировки."""
    model_config = {"extra": "forbid"}  # Запрещаем доп.параметры.

    limit: int = Field(default=100, ge=0)
    offset: int = Field(default=0, ge=0)
    order_by: str = "created_at"
