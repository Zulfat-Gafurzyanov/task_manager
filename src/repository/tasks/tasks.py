from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Task
from src.model.filters import TaskFilterParams
from src.repository.tasks.dto import (
    # DocumentDTO,
    StatusDTO,
    TagCreateDTO, TagResponseDTO,
    TaskCreateDTO, TaskResponseDTO, TaskUpdateDTO
)


class TaskRepository:
    """
    Репозиторий для работы с задачами в базе данных.

    Предоставляет CRUD-операции для Status, Tag, Task, работая с DTO-объектами.
    Изолирует бизнес-логику от реализации базы данных.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # Статус:
    async def get_all_statuses(self) -> list[StatusDTO]:
        """Получает все статусы."""
        query = text("""
            SELECT id, name
            FROM status
        """)
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [StatusDTO(id=row.id, name=row.name) for row in rows]

    async def get_status_by_id(self, status_id: int) -> StatusDTO:  # Нужен ли для API? Или нужен внутри?
        """Получает статус по его идентефикатору."""
        query = text("""
            SELECT id, name
            FROM status
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": status_id})
        row = result.fetchone()
        if not row:
            raise ValueError(f'Статус с id: {status_id} не найден')
        return StatusDTO(id=row.id, name=row.name)

    # Теги:
    async def create_tag(self, data: TagCreateDTO) -> TagResponseDTO:
        """Cоздает тег."""
        query = text("""
            INSERT INTO tag (name)
            VALUES (:name)
            RETURNING id, name
        """)
        result = await self.session.execute(query, {"name": data.name})
        row = result.fetchone()
        if not row:
            raise RuntimeError("БД не вернула данные после создания тега.")

        return TagResponseDTO(id=row.id, name=row.name)

    async def delete_tag(self, tag_id: int) -> None:
        """Удаляет тег."""
        async with self.session.begin():
            query = text("""
                DELETE
                FROM tag
                WHERE id = :id
                RETURNING id
            """)
            result = await self.session.execute(query, {"id": tag_id})
            row = result.fetchone()
            if not row:
                raise ValueError(f"Тег с id: {tag_id} не найден")

    # Задачи:
    async def create_task(self, data: TaskCreateDTO) -> TaskResponseDTO:
        """Создает задачу."""
        async with self.session.begin():
            # Создаём задачу (только базовые поля).
            query = text("""
                INSERT INTO task (
                    name, description, deadline_start, deadline_end, status_id
                )
                VALUES (
                    :name, :description, :deadline_start, :deadline_end,
                    :status_id
                )
                RETURNING id, name, description, deadline_start, deadline_end,
                    status_id
            """)
            result = await self.session.execute(
                query,
                {
                    "name": data.name,
                    "description": data.description,
                    "deadline_start": data.deadline_start,
                    "deadline_end": data.deadline_end,
                    "status_id": data.status_id,
                }
            )
            row = result.fetchone()
            if row is None:
                raise RuntimeError(
                    "БД не вернула данные после создания задачи.")
            
            # TODO: изучить JOIN, чтобы не делать еще 1 запрос.

            # Проверяем есть ли статус у задачи:
            if row.status_id is not None:
                status_dto = await self.get_status_by_id(row.status_id)
            else:
                status_dto = None

        return TaskResponseDTO(
            id=row.id,
            name=row.name,
            description=row.description,
            deadline_start=row.deadline_start,
            deadline_end=row.deadline_end,
            status=status_dto
        )


# TODO: в чтении добавить фильтры.
    # async def read_all_tasks(
    #         self, filters: TaskFilterParams) -> list[TaskResponseDTO]:
    #     """Получает все задачи с учётом фильтров."""

    #     query_str = f"""
    #         SELECT
    #             id,
    #             name,
    #             description,
    #             deadline_start,
    #             deadline_end,
    #             status_id
    #         FROM task
    #         ORDER BY {filters.order_by} {filters.order_direction.upper()}
    #         LIMIT :limit
    #         OFFSET :offset
    #     """
    #     query = text(query_str)
    #     result = await self.session.execute(
    #         query,
    #         {"limit": filters.limit, "offset": filters.offset}
    #     )
    #     tasks_rows = result.fetchall()
    #     tasks = []

    #     for row in tasks_rows:
    #         tasks.append(TaskResponseDTO(
    #             id=row.id,
    #             name=row.name,
    #             description=row.description,
    #             deadline_start=row.deadline_start,
    #             deadline_end=row.deadline_end,
    #             status=None,
    #             tags=[],
    #             documents=[]
    #         ))

    #     return tasks

    # async def read_task_by_id(self, task_id: int) -> TaskResponseDTO | None:
    #     """Получает задачу по его id."""
    #     pass

    # async def update_task(
    #         self, task_id: int, data: TaskUpdateDTO) -> TaskResponseDTO | None:
    #     """Обновляет поля задачи."""
    #     pass

    # async def delete_task(self, task_id: int) -> bool:
    #     """Удаляет задачу. Возвращает True, если задача удалена."""
    #     pass


# TODO:
# создать метод get_task_by_name
