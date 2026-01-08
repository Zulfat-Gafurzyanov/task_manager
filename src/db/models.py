from datetime import datetime

from sqlmodel import Field, SQLModel


# ???
# Как осуществить абстракцию? У меня все на SQLModel.
class Task(SQLModel, table=True):
    """Модель задачи для хранения в базе данных."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # ??? По какой логике расставляются индексы? Нужно ли на все поля?
    description: str | None = Field(default=None)
    deadline: datetime | None = Field(default=None)
    status: bool = Field(default=True)  # True - активная задача.
    created_at: datetime

# ???
# Здесь валидация полей тоже нужна? Или ее достаточно на получении данных от клиента?
# в папке model.
