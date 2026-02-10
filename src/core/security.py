import datetime as dt
import json
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes
)
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from src.core.encryption import Encryption
from src.core.keys import Keys
from src.model.users import UserBase
from src.model.api_schemas import (
    SignInRequest, SignUpRequest, TokenResponse
)
from src.repository.cache import CacheRepository
from src.repository.users.dto import UserCreateDTO
from src.repository.users.users import UserRepository
from src.api.v1.dependencies import get_user_repository, get_cache_repository

bearer_scheme = HTTPBearer()

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=131072,
    argon2__parallelism=4,
    argon2__time_cost=3,
)

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE = 1  # в часах
REFRESH_TOKEN_EXPIRE = 168

ROLE_SCOPES = {
    "user": ["tasks:read", "tasks:write"],
    "admin": ["tasks:read", "tasks:write", "admin"],
}


def _get_password_hash(password: str) -> str:
    """Хеширует пароль с использованием Argon2."""
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)


class Security:
    """
    Класс для работы с авторизацией и аутентификацией.

    Предоставляет методы управления пользователями и токенами:

    Аутентификация:
        - sign_in: вход по логину и паролю
        - signout: выход (удаление refresh-токенов)
        - get_current_user: получение текущего пользователя из токена

    Токены:
        - create_tokens: создание пары access + refresh
        - refresh_tokens: обновление токенов по refresh-токену

    Пользователи:
        - create_user: регистрация нового пользователя
        - update_user_password: смена пароля
    """

    @staticmethod
    async def _create_token(
        user_id: int,
        token_type: str,
        token_expire: int,
        scopes: list[str],
        cache_repo: CacheRepository | None = None,
    ) -> str:
        """Создаёт JWT-токен (access или refresh)."""
        now = dt.datetime.now(dt.UTC)
        jti = str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "exp": now + dt.timedelta(hours=token_expire),
            "iat": now,
            "jti": jti,
            "type": token_type,
            "scopes": scopes,
        }

        token = jwt.encode(
            payload, Keys.get_private_key(), algorithm=ALGORITHM
        )

        # Refresh-токен сохраняем в Redis для возможности отзыва.
        if token_type == "refresh" and cache_repo:
            ttl = int(dt.timedelta(hours=token_expire).total_seconds())
            await cache_repo.setex(
                cache_repo.key_token(user_id, jti), ttl, token
            )

        return token

    @classmethod
    async def create_tokens(
        cls, user_id: int, role: str, cache_repo: CacheRepository | None = None
    ) -> tuple[str, str]:
        """Создаёт пару access + refresh токенов для пользователя."""
        scope_names = ROLE_SCOPES.get(role, [])

        access_token = await cls._create_token(
            user_id, "access", ACCESS_TOKEN_EXPIRE, scope_names
        )
        refresh_token = await cls._create_token(
            user_id, "refresh", REFRESH_TOKEN_EXPIRE, scope_names, cache_repo
        )

        return access_token, refresh_token

    @classmethod
    async def refresh_tokens(
        cls,
        refresh_token: str,
        user_repo: UserRepository,
        cache_repo: CacheRepository,
    ) -> TokenResponse:
        """Обновляет токены по валидному refresh-токену."""
        user_id, _, token_jti = await cls._decode_token(
            refresh_token, require_refresh=True
        )

        if token_jti is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Неверные учетные данные.",
            )

        key = cache_repo.key_token(user_id, token_jti)
        if await cache_repo.get(key) is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Сессия истекла.",
            )

        user_dto = await user_repo.get_user_by_user_id(user_id)
        await cache_repo.delete(key)

        access, refresh = await cls.create_tokens(
            user_id, user_dto.role, cache_repo
        )
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
        )

    @classmethod
    async def sign_in(
        cls,
        form_data: SignInRequest,
        user_repo: UserRepository,
        cache_repo: CacheRepository,
    ) -> TokenResponse:
        """Проверяет логин и пароль, возвращает токены."""
        try:
            user_dto = await user_repo.get_user_by_login(form_data.username)
        except ValueError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Неверный логин или пароль.",
            )

        if not _verify_password(form_data.password, user_dto.hashed_password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Неверный логин или пароль.",
            )

        access, refresh = await cls.create_tokens(
            user_dto.id, user_dto.role, cache_repo
        )
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
        )

    @classmethod
    async def _decode_token(
        cls, token: str, require_refresh: bool = False
    ) -> tuple[int, list[str], str | None]:
        """Декодирует и валидирует JWT-токен."""
        try:
            payload = jwt.decode(
                token, Keys.get_public_key(), algorithms=[ALGORITHM]
            )

            if require_refresh and payload.get("type") != "refresh":
                raise PyJWTError()

            user_id = payload.get("sub")
            if user_id is None:
                raise PyJWTError()

            return int(user_id), payload.get("scopes", []), payload.get("jti")

        except PyJWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Неверные учетные данные."
            ) from None

    @staticmethod
    async def _check_scopes(
        security_scopes: SecurityScopes,
        token_scopes: list[str]
    ) -> None:
        """
        Проверяет наличие нужных scopes в токене.
        """
        if not security_scopes.scopes:
            return

        missing = set(security_scopes.scopes) - set(token_scopes)
        if missing:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Недостаточно прав."
            )

    @classmethod
    async def get_current_user(
        cls,
        access: Annotated[
            HTTPAuthorizationCredentials, Depends(bearer_scheme)
        ],
        security_scopes: SecurityScopes,
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)]
    ) -> UserBase:
        """Dependency: извлекает текущего пользователя из access-токена."""
        user_id, token_scopes, _ = await cls._decode_token(access.credentials)
        await cls._check_scopes(security_scopes, token_scopes)

        cache_key = cache_repo.key_user(user_id)
        cached = await cache_repo.get(cache_key)
        if cached:
            return UserBase(**json.loads(cached))

        user_dto = await user_repo.get_user_by_user_id(user_id)
        user = UserBase.model_validate(user_dto)

        await cache_repo.setex(
            cache_key,
            3600,
            json.dumps(user.model_dump())
        )

        return user

    @classmethod
    async def create_user(
        cls,
        data: SignUpRequest,
        user_repo: UserRepository,
    ) -> UserBase:
        """Создаёт пользователя с хешем пароля и зашифрованными email/phone."""
        try:
            dto = UserCreateDTO(
                username=data.username,
                password=_get_password_hash(data.password),
                email=await Encryption.encrypt_value(data.email),
                phone=await Encryption.encrypt_value(data.phone),
            )
            user_dto = await user_repo.create_user(dto)
            return UserBase.model_validate(user_dto)
        except ValueError as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    @classmethod
    async def signout(cls, user_id: int, cache_repo: CacheRepository) -> None:
        """Удаляет все refresh-токены пользователя из Redis."""
        await cache_repo.delete_by_pattern(f"user:{user_id}:token:*")

    @classmethod
    async def update_user_password(
        cls, user_id: int, new_password: str, user_repo: UserRepository
    ) -> None:
        """Обновляет пароль пользователя."""
        hashed_password = _get_password_hash(new_password)
        await user_repo.update_user_password_by_user_id(
            user_id, hashed_password)
