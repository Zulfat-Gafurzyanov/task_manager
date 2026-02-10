from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from exception.exceptions import (
    ResourceNotCreatedException,
    ResourceByIdNotFoundException,
    ResourceByNameNotFoundException
)
from src.repository.users.dto import (
    UserCreateDTO,
    UserResponseDTO,
    UserWithEmailAndPasswordDTO
)


class UserRepository:
    """
    Репозиторий для работы с пользователями в базе данных.

    Предоставляет CRUD-операции, работая с DTO-объектами:

    User:
        - get_user_by_login: получение пользователя по логину
        - get_user_by_user_id: получение пользователя по ID
        - create_user: создание пользователя
        - update_user_password_by_user_id: обновление пароля пользователя
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_login(
        self, username: str
    ) -> UserWithEmailAndPasswordDTO:
        """Получает пользователя по логину (для авторизации)."""
        query = text("""
            SELECT id, username, email, password, role
            FROM "user"
            WHERE username = :username
        """)
        result = await self.session.execute(query, {"username": username})
        row = result.fetchone()

        if not row:
            raise ResourceByNameNotFoundException("Пользователь", username)

        return UserWithEmailAndPasswordDTO(
            id=row.id,
            username=row.username,
            email=row.email,
            hashed_password=row.password,
            role=row.role
        )

    async def get_user_by_user_id(self, user_id: int) -> UserResponseDTO:
        """Получает пользователя по id."""
        query = text("""
            SELECT id, username, role
            FROM "user"
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": user_id})
        row = result.fetchone()

        if not row:
            raise ResourceByIdNotFoundException("Пользователь", user_id)

        return UserResponseDTO(
            id=row.id,
            username=row.username,
            role=row.role
        )

    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        """Создаёт пользователя."""
        async with self.session.begin():
            query = text("""
                INSERT INTO "user" (username, password, email, phone, role)
                VALUES (:username, :password, :email, :phone, :role)
                RETURNING id, username, role
            """)
            result = await self.session.execute(
                query,
                {
                    "username": data.username,
                    "password": data.password,
                    "email": data.email,
                    "phone": data.phone,
                    "role": data.role
                }
            )
            row = result.fetchone()
            if not row:
                raise ResourceNotCreatedException("Пользователя")

            return UserResponseDTO(
                id=row.id,
                username=row.username,
                role=row.role
            )

    async def update_user_password_by_user_id(
        self, user_id: int, hashed_password: str
    ) -> None:
        """Обновляет хеш пароля пользователя."""
        async with self.session.begin():
            query = text("""
                UPDATE "user"
                SET password = :password
                WHERE id = :id
                RETURNING id
            """)
            result = await self.session.execute(query, {
                "id": user_id,
                "password": hashed_password,
            })
            row = result.fetchone()

            if not row:
                raise ResourceByIdNotFoundException("Пользователь", user_id)
