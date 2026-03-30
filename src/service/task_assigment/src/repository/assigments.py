from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AssignmentRepository:
    """
    Репозиторий для работы с назначениями пользователей к задачам.

    Предоставляет операции назначения, работая напрямую с БД микросервиса.

    Assignment:
        - add: назначить пользователя на задачу
        - remove: снять пользователя с задачи
        - list: получить список назначенных пользователей
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task_id: int, user_id: int) -> None:
        """Назначить пользователя на задачу."""
        async with self.session.begin():
            query = text("""
                INSERT INTO taskassigment (task_id, user_id)
                VALUES (:task_id, :user_id)
            """)
            await self.session.execute(
                query,
                {"task_id": task_id, "user_id": user_id}
            )

    async def remove(self, task_id: int, user_id: int) -> None:
        """Снять пользователя с задачи."""
        async with self.session.begin():
            query = text("""
                DELETE FROM taskassigment
                WHERE task_id = :task_id AND user_id = :user_id
            """)
            await self.session.execute(
                query,
                {"task_id": task_id, "user_id": user_id}
            )

    async def list(self, task_id: int) -> list[int]:
        """Получить список назначенных пользователей."""
        query = text("""
            SELECT user_id FROM taskassigment
            WHERE task_id = :task_id
        """)
        result = await self.session.execute(query, {"task_id": task_id})
        return [row.user_id for row in result.fetchall()]
