from sqlalchemy.exc import IntegrityError

from src.core.security import Security
from src.exception.exceptions import (
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    AuthenticationException
)
from src.model.users import TokenResponse, UserBase, UserCreate, UserLogin
from src.repository.users.dto import UserCreateDTO
from src.repository.users.users import UserRepository


class UserService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, data: UserCreate) -> UserBase:
        try:
            hashed_password = Security.hash_password(data.password)
            user_dto = UserCreateDTO(
                username=data.username,
                hashed_password=hashed_password
            )
            created_user = await self.user_repo.create_user(user_dto)
            return UserBase(**created_user.model_dump())
        except IntegrityError:
            raise ResourceAlreadyExistsException("Пользователь", data.username)

    async def login_user(self, data: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_user_by_username(data.username)
        if not user or not Security.verify_password(
            data.password,
            user.password
        ):
            raise AuthenticationException()
        # Создаем токены
        access_token, refresh_token = await Security.create_tokens(user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        _, access_token, new_refresh_token = await Security.update_tokens(
            refresh_token
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    async def get_user_by_id(self, user_id: int) -> UserBase:
        """Получить пользователя по ID."""
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("Пользователь", user_id)
        return UserBase(**user.model_dump())
