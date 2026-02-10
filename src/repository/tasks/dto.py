import datetime

from pydantic import BaseModel, Field


class DocumentCreateDTO(BaseModel):
    """DTO для создания документа."""
    name: str
    path: str
    task_id: int


class DocumentDTO(BaseModel):
    """DTO для документа."""
    id: int
    name: str
    path: str


class StatusDTO(BaseModel):
    """DTO для статуса."""
    id: int
    name: str


class TagCreateDTO(BaseModel):
    """DTO для создания тега."""
    name: str
    user_id: int


class TagResponseDTO(BaseModel):
    """DTO для возврата тега."""
    id: int
    name: str


class TaskCreateDTO(BaseModel):
    """DTO для создания задачи."""
    name: str
    description: str | None = None
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None
    user_id: int


class TaskResponseDTO(BaseModel):
    """DTO для возвращения задачи."""
    id: int
    name: str
    description: str | None
    deadline_start: datetime.date | None
    deadline_end: datetime.date | None
    status: StatusDTO | None
    tags: list[TagResponseDTO] = Field(default_factory=list)
    documents: list[DocumentDTO] = Field(default_factory=list)


class TaskUpdateDTO(BaseModel):
    """DTO для изменения задачи."""
    name: str | None = None
    description: str | None = None
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None
    tags: list[TagResponseDTO] | None = None
