from src.core.encryption import Encryption
from src.model.users import (
    UserBaseSchema,
    UserBaseWithPasswordAndEmail,
    UserBaseWithUUIDSchema
)
from src.model.tokens import RulesSchema
from src.repository.users.users import UserRepository
from src.repository.users.dto import UserCreateDTO


class UserService:
    """
    Сервисный слой для работы с пользователями.

    Описывает бизнес-логику управления пользователями,
    включая расшифровку чувствительных данных и работу с ролями.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_login_with_password(
        self, username: str
    ) -> UserBaseWithPasswordAndEmail:
        """
        Получает пользователя по логину с паролем и расшифрованным email.
        Используется для аутентификации.
        """
        user_dto = await self.user_repo.get_user_by_login(username)
        # Расшифровываем email:
        decrypted_email = await Encryption.decrypt_value(user_dto.email)

        return UserBaseWithPasswordAndEmail(
            id=user_dto.id,
            username=user_dto.username,
            email=decrypted_email,
            password=user_dto.password
        )

    async def get_user_by_id(self, user_id: int) -> UserBaseSchema:
        user_dto = await self.user_repo.get_user_by_user_id(user_id)
        return UserBaseSchema.model_validate(user_dto)

    async def get_user_with_uuid(self, user_id: int) -> UserBaseWithUUIDSchema:
        user_dto = await self.user_repo.get_user_with_uuid_by_user_id(user_id)
        return UserBaseWithUUIDSchema.model_validate(user_dto)

    async def get_user_rules(self, user_id: int) -> RulesSchema:
        """Получает список ролей пользователя."""
        rules_dto = await self.user_repo.get_available_rules_for_user(user_id)
        return RulesSchema.model_validate(rules_dto)

    async def create_user_with_encrypted_data(
        self, data: UserCreateDTO
    ) -> UserBaseSchema:
        """Создаёт пользователя с уже зашифрованными данными."""
        user_dto = await self.user_repo.create_user_with_rules(data)
        return UserBaseSchema.model_validate(user_dto)

    async def update_user_password(
        self, user_id: int, hashed_password: str
    ) -> None:
        """Обновляет хеш пароля пользователя."""
        await self.user_repo.update_user_password_by_user_id(
            user_id, hashed_password
        )
