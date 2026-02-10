import datetime
from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StatusResponse(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=64)

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str = Field(max_length=64)


class TagResponse(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=64)

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    name: str = Field(max_length=512)
    description: str | None = Field(default=None, max_length=2048)
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None

    @model_validator(mode='after')
    def check_deadline(self) -> Self:
        """Проверка, что дата начала раньше даты окончания."""
        if self.deadline_start and self.deadline_end:
            if self.deadline_start > self.deadline_end:
                raise ValueError(
                    'Дата окончания не может быть раньше даты начала')
        return self

    @model_validator(mode='after')
    def check_dates_not_in_past(self) -> Self:
        """Проверка, что даты не в прошлом."""
        today = datetime.date.today()
        if self.deadline_start and self.deadline_start < today:
            raise ValueError('Дата начала не может быть в прошлом')
        if self.deadline_end and self.deadline_end < today:
            raise ValueError('Дата окончания не может быть в прошлом')
        return self


class DocumentResponse(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=128)
    path: str = Field(max_length=256)

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(max_length=512)
    description: str | None = Field(default=None, max_length=2048)
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status: StatusResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)
    documents: list[DocumentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    """
    Модель для обновления существующей задачи.
    Все поля опциональны - обновляются только переданные значения.
    """
    name: str | None = Field(default=None, max_length=512)
    description: str | None = Field(default=None, max_length=2048)
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None

    @model_validator(mode='after')
    def check_deadline(self) -> Self:
        """Проверка, что дата начала раньше даты окончания."""
        if self.deadline_start and self.deadline_end:
            if self.deadline_start > self.deadline_end:
                raise ValueError(
                    'Дата окончания не может быть раньше даты начала')
        return self
