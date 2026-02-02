from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users.dto import (
    UserCreateDTO,
    UserResponseDTO,
    UserWithEmailDTO,
    UserWithPasswordAndEmailDTO,
    UserWithUUIDDTO,
    UserRulesDTO, RuleDTO,
)


class UserRepository:
    """
    Репозиторий для работы с пользователями в базе данных.
    Предоставляет CRUD-операции для User и связанных ролей (Rule).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_login(self, username: str) -> UserWithPasswordAndEmailDTO:
        """Получает пользователя по логину (для авторизации)."""

        query = text("""
            SELECT id, username, email, password
            FROM "user"
            WHERE username = :username
        """)
        result = await self.session.execute(query, {"username": username})
        row = result.fetchone()
        if not row:
            raise ValueError(f'Пользователь с логином "{username}" не найден.')

        return UserWithPasswordAndEmailDTO(
            id=row.id, username=row.username, email=row.email, password=row.password
        )

    async def get_user_by_user_id(self, user_id: int) -> UserResponseDTO:
        """Получает пользователя по id."""

        query = text("""
            SELECT id, username
            FROM "user"
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": user_id})
        row = result.fetchone()
        if not row:
            raise ValueError(f"Пользователь с id={user_id} не найден.")

        return UserResponseDTO(id=row.id, username=row.username)

    async def get_user_with_uuid_by_user_id(self, user_id: int) -> UserWithUUIDDTO:
        """Получает пользователя с UUID по id."""

        query = text("""
            SELECT id, username, uuid
            FROM "user"
            WHERE id = :id
        """)
        result = await self.session.execute(query, {"id": user_id})
        row = result.fetchone()
        if not row:
            raise ValueError(f"Пользователь с id={user_id} не найден.")

        return UserWithUUIDDTO(id=row.id, username=row.username, uuid=row.uuid)

    async def get_available_rules_for_user(self, user_id: int) -> UserRulesDTO:
        """Получает все роли пользователя через связующую таблицу."""

        query = text("""
            SELECT r.name
            FROM rule r
            JOIN userrule ur ON ur.rule_id = r.id
            WHERE ur.user_id = :user_id
        """)
        result = await self.session.execute(query, {"user_id": user_id})
        rows = result.fetchall()
        rules = [RuleDTO(name=row.name) for row in rows]

        return UserRulesDTO(rules=rules)

    async def create_user_with_rules(self, data: UserCreateDTO) -> UserResponseDTO:
        """Создаёт пользователя и привязывает роли."""

        async with self.session.begin():
            # Создаём пользователя.
            query = text("""
                INSERT INTO "user" (username, password, email, phone)
                VALUES (:username, :password, :email, :phone)
                RETURNING id, username
            """)
            result = await self.session.execute(query, {
                "username": data.username,
                "password": data.password,
                "email": data.email,
                "phone": data.phone,
            })
            row = result.fetchone()
            if not row:
                raise RuntimeError("БД не вернула данные после создания пользователя.")

            user_id = row.id

            # Привязываем роли по именам.
            for rule_name in data.rules:
                rule_query = text("""
                    SELECT id
                    FROM rule
                    WHERE name = :name
                """)
                rule_result = await self.session.execute(
                    rule_query, {"name": rule_name}
                )
                rule_row = rule_result.fetchone()
                if not rule_row:
                    raise ValueError(f'Роль "{rule_name}" не найдена.')

                link_query = text("""
                    INSERT INTO userrule (user_id, rule_id)
                    VALUES (:user_id, :rule_id)
                """)
                await self.session.execute(link_query, {
                    "user_id": user_id,
                    "rule_id": rule_row.id,
                })

        return UserResponseDTO(id=row.id, username=row.username)

    async def update_user_password_by_user_id(
        self, user_id: int, hashed_password: str
    ) -> None:
        """Обновляет хеш пароля пользователя."""

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
            raise ValueError(f"Пользователь с id={user_id} не найден.")

# Не хватает return