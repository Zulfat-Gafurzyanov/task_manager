import logging

from src.celery_app.celery_tasks import send_welcome_email
from src.core.encryption import Encryption
from src.core.password import get_password_hash
from src.model.api_schemas import SignUpRequest
from src.model.users import UserBase
from src.repository.users.users import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервисный слой для работы с пользователями.

    Описывает бизнес-логику управления пользователями,
    взаимодействуя с репозиторием через DTO-объекты.

    User:
        - get_user_by_id: получение пользователя по ID
        - get_user_by_login: получение пользователя по логину
        - register: регистрация нового пользователя
        - update_password: обновление пароля пользователя
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: int) -> UserBase:
        """Получает пользователя по ID."""
        user_dto = await self.user_repo.get_user_by_user_id(user_id)
        return UserBase.model_validate(user_dto)

    async def get_user_by_login(self, username: str) -> UserBase:
        """Получает пользователя по логину."""
        user_dto = await self.user_repo.get_user_by_login(username)
        return UserBase.model_validate(user_dto)

    async def register(self, data: SignUpRequest) -> UserBase:
        """Регистрирует нового пользователя: хеширует пароль,
        шифрует email/phone, сохраняет в БД и отправляет приветственное письмо.
        """
        from src.repository.users.dto import UserCreateDTO
        dto = UserCreateDTO(
            username=data.username,
            password=get_password_hash(data.password),
            email=await Encryption.encrypt_value(data.email),
            phone=await Encryption.encrypt_value(data.phone),
        )
        user_dto = await self.user_repo.create_user(dto)
        logger.info("Пользователь зарегистрирован: username=%s", data.username)

        # Отправляем письмо на почту:
        send_welcome_email.delay(data.username, data.email)

        return UserBase.model_validate(user_dto)

    async def update_password(
        self, user_id: int, new_password: str
    ) -> None:
        """Хеширует новый пароль и обновляет его в БД."""
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update_user_password_by_user_id(
            user_id, hashed_password
        )
