import datetime

from pydantic import BaseModel


class DocumentDTO(BaseModel):
    """DTO для документа."""
    id: int
    name: str
    path: str


class StatusDTO(BaseModel):
    """DTO для статуса."""
    id: int
    name: str


class TagDTO(BaseModel):
    """DTO для тега."""
    id: int
    name: str


class TaskCreateDTO(BaseModel):
    """DTO для создания задачи."""
    name: str
    description: str | None = None
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None


class TaskResponseDTO(BaseModel):
    """DTO для возвращения задачи."""
    id: int
    name: str
    description: str | None
    deadline_start: datetime.date | None
    deadline_end: datetime.date | None
    # В ответе (если были созданы) получаем объекты со всеми полями:
    status: StatusDTO | None
    tags: list[TagDTO] = []
    documents: list[DocumentDTO] = []


class TaskUpdateDTO(BaseModel):
    """DTO для изменения задачи."""
    name: str | None = None
    description: str | None = None
    deadline_start: datetime.date | None = None
    deadline_end: datetime.date | None = None
    status_id: int | None = None
    tag_ids: list[int] | None = None
    document_ids: list[int] | None = None
