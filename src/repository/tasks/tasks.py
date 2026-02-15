from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exception.exceptions import (
    ResourceAlreadyExistsException,
    ResourceByIdNotFoundException,
    ResourceNotCreatedException
)
from src.model.filters import TaskFilterParams
from src.repository.tasks.dto import (
    DocumentCreateDTO, DocumentDTO,
    StatusDTO,
    TagCreateDTO, TagResponseDTO,
    TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
)


class TaskRepository:
    """
    Репозиторий для работы с задачами в базе данных.

    Предоставляет CRUD-операции, работая с DTO-объектами.
    Все операции с задачами, тегами и документами
    проверяют принадлежность ресурса пользователю (user_id).

    Status:
        - get_all_statuses: получение всех статусов
        - get_status_by_id: получение статуса по ID

    Tag:
        - create_tag: создание тега
        - delete_tag: удаление тега

    Task:
        - check_task_ownership: проверка принадлежности задачи пользователю
        - create_task: создание задачи
        - get_all_tasks: получение задач пользователя
        - get_task_by_id: получение задачи по ID
        - update_task: обновление задачи
        - delete_task: удаление задачи

    TaskTag:
        - get_task_tags: получение тегов задачи
        - add_tag_to_task: добавление тега к задаче
        - remove_tag_from_task: удаление тега у задачи

    Document:
        - create_document: создание документа
        - get_task_documents: получение документов задачи
        - delete_document: удаление документа
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ===== Status =====

    async def get_all_statuses(self) -> list[StatusDTO]:
        """Получает все статусы."""
        query = text("""
            SELECT id, name
            FROM status
        """)
        result = await self.session.execute(query)
        rows = result.fetchall()

        return [
            StatusDTO(
                id=row.id,
                name=row.name
            ) for row in rows
        ]

    async def get_status_by_id(self, status_id: int) -> StatusDTO:
        """Получает статус по его идентефикатору."""
        query = text("""
            SELECT id, name
            FROM status
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": status_id})
        row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Статус", status_id)

        return StatusDTO(
            id=row.id,
            name=row.name
        )

    # ===== Tag =====

    async def create_tag(self, data: TagCreateDTO) -> TagResponseDTO:
        """Cоздает тег."""
        try:
            async with self.session.begin():
                query = text("""
                    INSERT INTO tag (name, user_id)
                    VALUES (:name, :user_id)
                    RETURNING id, name
                """)
                result = await self.session.execute(
                    query, {"name": data.name, "user_id": data.user_id}
                )
                row = result.fetchone()
        except IntegrityError:
            raise ResourceAlreadyExistsException("Тег", data.name)

        if not row:
            raise ResourceNotCreatedException("Тег")

        return TagResponseDTO(
            id=row.id,
            name=row.name
        )

    async def delete_tag(self, tag_id: int, user_id: int) -> None:
        """Удаляет тег (только если принадлежит пользователю)."""
        async with self.session.begin():
            query = text("""
                DELETE FROM tag
                WHERE id = :id AND user_id = :user_id
                RETURNING id
            """)
            result = await self.session.execute(
                query, {"id": tag_id, "user_id": user_id}
            )
            row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Тег", tag_id)

    # ===== Task =====

    async def create_task(self, data: TaskCreateDTO) -> TaskResponseDTO:
        """Создает задачу."""
        async with self.session.begin():
            query = text("""
                WITH new_task AS (
                    INSERT INTO task (
                        name, description, deadline_start,
                        deadline_end, status_id, user_id
                    )
                    VALUES (
                        :name, :description, :deadline_start,
                        :deadline_end, :status_id, :user_id
                    )
                    RETURNING id, name, description, deadline_start,
                        deadline_end, status_id
                )
                SELECT
                    new_task.id, new_task.name, new_task.description,
                    new_task.deadline_start, new_task.deadline_end,
                    status.id as status_id, status.name as status_name
                FROM new_task
                LEFT JOIN status ON new_task.status_id = status.id
            """)
            result = await self.session.execute(
                query,
                {
                    "name": data.name,
                    "description": data.description,
                    "deadline_start": data.deadline_start,
                    "deadline_end": data.deadline_end,
                    "status_id": data.status_id,
                    "user_id": data.user_id,
                }
            )
            row = result.fetchone()

        if not row:
            raise ResourceNotCreatedException("Задачу")

        # Формируем статус, если он есть
        status_dto = None
        if row.status_id:
            status_dto = StatusDTO(
                id=row.status_id,
                name=row.status_name
            )

        return TaskResponseDTO(
            id=row.id,
            name=row.name,
            description=row.description,
            deadline_start=row.deadline_start,
            deadline_end=row.deadline_end,
            status=status_dto
        )

    async def get_all_tasks(
        self, filters: TaskFilterParams, user_id: int
    ) -> list[TaskResponseDTO]:
        """Получает задачи пользователя с фильтрами."""
        query = text(f"""
            SELECT
                task.id, task.name, task.description,
                task.deadline_start, task.deadline_end,
                status.id as status_id, status.name as status_name
            FROM task
            LEFT JOIN status ON task.status_id = status.id
            WHERE task.user_id = :user_id
            ORDER BY task.{filters.order_by} {filters.order_direction}
            LIMIT :limit OFFSET :offset
        """)
        result = await self.session.execute(
            query,
            {
                "user_id": user_id,
                "limit": filters.limit,
                "offset": filters.offset,
            }
        )
        rows = result.fetchall()

        tasks = []
        for row in rows:
            status_dto = None
            if row.status_id:
                status_dto = StatusDTO(
                    id=row.status_id,
                    name=row.status_name
                )

            tags = await self.get_task_tags(row.id, user_id)
            documents = await self.get_task_documents(row.id, user_id)

            tasks.append(TaskResponseDTO(
                id=row.id,
                name=row.name,
                description=row.description,
                deadline_start=row.deadline_start,
                deadline_end=row.deadline_end,
                status=status_dto,
                tags=tags,
                documents=documents
            ))

        return tasks

    async def check_task_ownership(
        self, task_id: int, user_id: int
    ) -> None:
        """Проверяет, что задача принадлежит пользователю."""
        query = text("""
            SELECT id FROM task
            WHERE id = :id AND user_id = :user_id
        """)
        result = await self.session.execute(
            query, {"id": task_id, "user_id": user_id}
        )
        row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Задача", task_id)

    async def get_task_by_id(
        self, task_id: int, user_id: int
    ) -> TaskResponseDTO:
        """Получает задачу по ID (только если принадлежит пользователю)."""
        query = text("""
            SELECT
                task.id, task.name, task.description,
                task.deadline_start, task.deadline_end,
                status.id as status_id, status.name as status_name
            FROM task
            LEFT JOIN status ON task.status_id = status.id
            WHERE task.id = :id AND task.user_id = :user_id
        """)
        result = await self.session.execute(
            query, {"id": task_id, "user_id": user_id}
        )
        row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Задача", task_id)

        status_dto = None
        if row.status_id:
            status_dto = StatusDTO(
                id=row.status_id,
                name=row.status_name
            )

        tags = await self.get_task_tags(task_id, user_id)
        documents = await self.get_task_documents(task_id, user_id)

        return TaskResponseDTO(
            id=row.id,
            name=row.name,
            description=row.description,
            deadline_start=row.deadline_start,
            deadline_end=row.deadline_end,
            status=status_dto,
            tags=tags,
            documents=documents
        )

    async def update_task(
        self, task_id: int, data: TaskUpdateDTO, user_id: int
    ) -> TaskResponseDTO:
        """Обновляет задачу (только если принадлежит пользователю)."""
        async with self.session.begin():
            # Формируем список только с теми полями, которые переданы
            update_fields = []
            params: dict[str, Any] = {"id": task_id, "user_id": user_id}

            if data.name is not None:
                update_fields.append("name = :name")
                params["name"] = data.name
            if data.description is not None:
                update_fields.append("description = :description")
                params["description"] = data.description
            if data.deadline_start is not None:
                update_fields.append("deadline_start = :deadline_start")
                params["deadline_start"] = data.deadline_start
            if data.deadline_end is not None:
                update_fields.append("deadline_end = :deadline_end")
                params["deadline_end"] = data.deadline_end
            if data.status_id is not None:
                update_fields.append("status_id = :status_id")
                params["status_id"] = data.status_id

            if not update_fields:
                return await self.get_task_by_id(
                    task_id, user_id
                )

            query = text(f"""
                UPDATE task
                SET {', '.join(update_fields)}
                WHERE id = :id AND user_id = :user_id
                RETURNING id
            """)
            result = await self.session.execute(query, params)
            row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Задача", task_id)

        return await self.get_task_by_id(task_id, user_id)

    async def delete_task(
        self, task_id: int, user_id: int
    ) -> None:
        """Удаляет задачу (только если принадлежит пользователю)."""
        async with self.session.begin():
            query = text("""
                DELETE FROM task
                WHERE id = :id AND user_id = :user_id
                RETURNING id
            """)
            result = await self.session.execute(
                query, {"id": task_id, "user_id": user_id}
            )
            row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Задача", task_id)

    # ===== TaskTag =====

    async def get_task_tags(
        self, task_id: int, user_id: int
    ) -> list[TagResponseDTO]:
        """Получает все теги задачи."""
        query = text("""
            SELECT tag.id, tag.name
            FROM tag
            INNER JOIN tasktag ON tag.id = tasktag.tag_id
            INNER JOIN task ON tasktag.task_id = task.id
            WHERE tasktag.task_id = :task_id AND task.user_id = :user_id
        """)
        result = await self.session.execute(
            query, {"task_id": task_id, "user_id": user_id}
        )
        rows = result.fetchall()

        return [
            TagResponseDTO(
                id=row.id,
                name=row.name
            ) for row in rows
        ]

    async def add_tag_to_task(
        self, task_id: int, tag_id: int, user_id: int
    ) -> None:
        """Добавляет тег к задаче."""
        try:
            async with self.session.begin():
                await self.check_task_ownership(task_id, user_id)

                # Проверяем что тег принадлежит пользователю
                check_query = text("""
                    SELECT id FROM tag
                    WHERE id = :tag_id AND user_id = :user_id
                """)
                result = await self.session.execute(
                    check_query,
                    {"tag_id": tag_id, "user_id": user_id}
                )
                if not result.fetchone():
                    raise ResourceByIdNotFoundException("Тег", tag_id)

                query = text("""
                    INSERT INTO tasktag (task_id, tag_id)
                    VALUES (:task_id, :tag_id)
                """)
                await self.session.execute(
                    query,
                    {"task_id": task_id, "tag_id": tag_id}
                )
        except IntegrityError:
            raise ResourceAlreadyExistsException(
                "Связь", f"задачи {task_id} с тегом {tag_id}"
            )

    async def remove_tag_from_task(
        self, task_id: int, tag_id: int, user_id: int
    ) -> None:
        """Удаляет тег у задачи."""
        async with self.session.begin():
            await self.check_task_ownership(task_id, user_id)

            query = text("""
                DELETE FROM tasktag
                WHERE task_id = :task_id AND tag_id = :tag_id
                RETURNING id
            """)
            result = await self.session.execute(
                query,
                {"task_id": task_id, "tag_id": tag_id}
            )
            row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException(
                "Связь задачи с тегом", tag_id
            )

    # ===== Document =====

    async def create_document(
        self, data: DocumentCreateDTO, user_id: int
    ) -> DocumentDTO:
        """Создает документ."""
        async with self.session.begin():
            await self.check_task_ownership(data.task_id, user_id)
            query = text("""
                INSERT INTO document (name, path, task_id)
                VALUES (:name, :path, :task_id)
                RETURNING id, name, path
            """)
            result = await self.session.execute(query, {
                "name": data.name,
                "path": data.path,
                "task_id": data.task_id,
            })
            row = result.fetchone()

        if not row:
            raise ResourceNotCreatedException("Документ")

        return DocumentDTO(
            id=row.id,
            name=row.name,
            path=row.path
        )

    async def get_task_documents(
        self, task_id: int, user_id: int
    ) -> list[DocumentDTO]:
        """Получает все документы задачи."""
        query = text("""
            SELECT document.id, document.name, document.path
            FROM document
            INNER JOIN task ON document.task_id = task.id
            WHERE document.task_id = :task_id AND task.user_id = :user_id
        """)
        result = await self.session.execute(
            query, {"task_id": task_id, "user_id": user_id}
        )
        rows = result.fetchall()

        return [
            DocumentDTO(
                id=row.id,
                name=row.name,
                path=row.path
            ) for row in rows
        ]

    async def delete_document(
        self, document_id: int, user_id: int
    ) -> DocumentDTO:
        """Удаляет документ (только если задача принадлежит пользователю)."""
        async with self.session.begin():
            query = text("""
                DELETE FROM document
                USING task
                WHERE document.id = :id
                    AND document.task_id = task.id
                    AND task.user_id = :user_id
                RETURNING document.id, document.name, document.path
            """)
            result = await self.session.execute(
                query,
                {"id": document_id, "user_id": user_id},
            )
            row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Документ", document_id)

        return DocumentDTO(
            id=row.id,
            name=row.name,
            path=row.path
        )
