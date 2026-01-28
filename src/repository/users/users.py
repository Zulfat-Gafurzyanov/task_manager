from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users.dto import (
    UserCreateDTO,
    UserDTO,
    UserWithPasswordDTO
)


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, data: UserCreateDTO) -> UserDTO:
        query = text("""
            INSERT INTO "user" (username, password)
            VALUES (:username, :password)
            RETURNING id, username
        """)
        result = await self.session.execute(
            query,
            {"username": data.username, "password": data.hashed_password}
        )
        row = result.fetchone()
        if not row:
            raise RuntimeError(
                "БД не вернула данные после создания пользователя.")
        return UserDTO(id=row.id, username=row.username)

    async def get_user_by_username(
        self, username: str
    ) -> UserWithPasswordDTO | None:
        query = text("""
            SELECT id, username, password
            FROM "user"
            WHERE username = :username
        """)
        result = await self.session.execute(query, {"username": username})
        row = result.fetchone()
        if not row:
            return None
        return UserWithPasswordDTO(
            id=row.id,
            username=row.username,
            password=row.password
        )

    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        query = text("""
            SELECT id, username
            FROM "user"
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": user_id})
        row = result.fetchone()
        if not row:
            return None
        return UserDTO(id=row.id, username=row.username)
