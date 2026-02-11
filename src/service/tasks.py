import json
import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from src.model.filters import TaskFilterParams
from src.model.tasks import (
    DocumentResponse,
    StatusResponse,
    TagCreate, TagResponse,
    TaskCreate, TaskResponse, TaskUpdate
)
from src.repository.tasks.dto import (
    DocumentCreateDTO,
    TagCreateDTO,
    TaskCreateDTO, TaskUpdateDTO
)
from src.repository.cache import CacheRepository
from src.repository.tasks.tasks import TaskRepository


class TaskService:
    """
    Сервисный слой для работы с задачами.

    Описывает бизнес-логику управления задачами,
    включая проверку прав доступа (владение ресурсом),
    кеширование и взаимодействие с репозиторием.

    Все операции проверяют принадлежность ресурса
    текущему пользователю через check_task_ownership.

    Status:
        - get_all_statuses: получение всех статусов

    Tag:
        - create_tag: создание тега пользователя
        - delete_tag: удаление тега пользователя

    Task:
        - create_task: создание задачи пользователя
        - get_all_tasks: получение задач пользователя
        - get_task_by_id: получение задачи по ID
        - update_task: обновление задачи
        - delete_task: удаление задачи

    TaskTag:
        - get_task_tags: получение тегов задачи
        - add_tag_to_task: привязка тега к задаче
        - remove_tag_from_task: удаление тега у задачи

    Document:
        - upload_document: загрузка документа
        - get_task_documents: получение документов задачи
        - delete_document: удаление документа
    """

    def __init__(self, task_repo: TaskRepository, cache_repo: CacheRepository):
        self.task_repo = task_repo
        self.cache_repo = cache_repo

    # ===== Status =====

    async def get_all_statuses(self) -> list[StatusResponse]:
        cache_key = self.cache_repo.key_all_statuses()
        cached = await self.cache_repo.get(cache_key)
        if cached:
            return [StatusResponse(**item) for item in json.loads(cached)]

        statuses = await self.task_repo.get_all_statuses()
        result = [StatusResponse.model_validate(status) for status in statuses]

        await self.cache_repo.setex(
            cache_key,
            3600,
            json.dumps([status.model_dump() for status in result])
        )
        return result

    # ===== Tag =====

    async def create_tag(self, data: TagCreate, user_id: int) -> TagResponse:
        tag_dto = TagCreateDTO(name=data.name, user_id=user_id)
        created_tag = await self.task_repo.create_tag(tag_dto)
        return TagResponse.model_validate(created_tag)

    async def delete_tag(self, tag_id: int, user_id: int) -> None:
        await self.task_repo.delete_tag(tag_id, user_id)

    # ===== Task =====

    async def create_task(
        self, data: TaskCreate, user_id: int
    ) -> TaskResponse:
        task_dto = TaskCreateDTO(
            name=data.name,
            description=data.description,
            deadline_start=data.deadline_start,
            deadline_end=data.deadline_end,
            status_id=data.status_id,
            user_id=user_id,
        )
        created_task = await self.task_repo.create_task(task_dto)
        return TaskResponse.model_validate(created_task)

    async def get_all_tasks(
        self, filters: TaskFilterParams, user_id: int
    ) -> list[TaskResponse]:
        tasks = await self.task_repo.get_all_tasks(filters, user_id)
        return [
            TaskResponse.model_validate(task)
            for task in tasks
        ]

    async def get_task_by_id(
        self, task_id: int, user_id: int
    ) -> TaskResponse:
        task = await self.task_repo.get_task_by_id(task_id, user_id)
        return TaskResponse.model_validate(task)

    async def update_task(
        self, task_id: int, data: TaskUpdate, user_id: int
    ) -> TaskResponse:
        task_dto = TaskUpdateDTO(
            **data.model_dump(exclude_unset=True)
        )
        updated_task = await self.task_repo.update_task(
            task_id, task_dto, user_id
        )
        return TaskResponse.model_validate(updated_task)

    async def delete_task(
        self, task_id: int, user_id: int
    ) -> None:
        await self.task_repo.delete_task(task_id, user_id)

    # ===== TaskTag =====

    async def get_task_tags(
            self, task_id: int, user_id: int) -> list[TagResponse]:
        await self.task_repo.check_task_ownership(task_id, user_id)
        tags = await self.task_repo.get_task_tags(task_id, user_id)
        result = [TagResponse.model_validate(tag) for tag in tags]
        return result

    async def add_tag_to_task(
        self, task_id: int, tag_id: int, user_id: int
    ) -> None:
        await self.task_repo.add_tag_to_task(task_id, tag_id, user_id)

    async def remove_tag_from_task(
        self, task_id: int, tag_id: int, user_id: int
    ) -> None:
        await self.task_repo.remove_tag_from_task(task_id, tag_id, user_id)

    # ===== Document =====

    async def upload_document(
        self, task_id: int, file: UploadFile, user_id: int
    ) -> DocumentResponse:
        """Сохраняет файл на диск и создает запись в БД."""
        # Сохраняем файл на диск
        file_path = Path(f"uploads/{task_id}/{uuid.uuid4()}_{file.filename}")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        file_path.write_bytes(content)

        # Создаем запись в БД
        doc_dto = DocumentCreateDTO(
            name=file.filename,
            path=str(file_path),
            task_id=task_id,
        )
        created_doc = await self.task_repo.create_document(doc_dto, user_id)
        return DocumentResponse.model_validate(created_doc)

    async def get_task_documents(
        self, task_id: int, user_id: int
    ) -> list[DocumentResponse]:
        """Получает список документов задачи."""
        await self.task_repo.check_task_ownership(task_id, user_id)
        documents = await self.task_repo.get_task_documents(
            task_id, user_id
        )
        return [
            DocumentResponse.model_validate(doc)
            for doc in documents
        ]

    async def delete_document(
        self, document_id: int, user_id: int
    ) -> None:
        """Удаляет документ из БД и с диска."""
        doc = await self.task_repo.delete_document(
            document_id, user_id
        )

        file_path = Path(doc.path)
        if file_path.exists():
            os.remove(file_path)
