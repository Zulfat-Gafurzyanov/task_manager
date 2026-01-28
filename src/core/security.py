import datetime as dt
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from src.constants.tokens import (
    ACCESS_TOKEN_EXPIRE,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE
)
from src.core.keys import Keys
from src.db.redis import redis_client

bearer_scheme = HTTPBearer()

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=131072,
    argon2__parallelism=4,
    argon2__time_cost=3,
)


def _get_password_hash(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)


class Security:
    @staticmethod
    async def _create_token(
        user_id: int,
        token_type: str,
        token_expire: int,
    ) -> str:
        """Создает JWT токен."""
        now = dt.datetime.now(dt.UTC)
        jti = str(uuid.uuid4())
        payload = {
            "sub": str(user_id),
            "exp": now + dt.timedelta(hours=token_expire),
            "iat": now,
            "jti": jti,
            "type": token_type,
        }
        token = jwt.encode(
            payload,
            Keys.get_private_key(),
            algorithm=ALGORITHM
        )
        # Refresh token сохраняем в Redis
        if token_type == "refresh":
            ttl = int(dt.timedelta(hours=token_expire).total_seconds())
            redis = redis_client.get_redis()
            await redis.setex(
                f"user:{user_id}:token:{jti}", ttl, token
            )
        return token

    @classmethod
    async def create_tokens(cls, user_id: int) -> tuple[str, str]:
        """Создает пару токенов для пользователя."""
        access_token = await cls._create_token(
            user_id, "access", ACCESS_TOKEN_EXPIRE
        )
        refresh_token = await cls._create_token(
            user_id, "refresh", REFRESH_TOKEN_EXPIRE
        )
        return access_token, refresh_token

    @classmethod
    async def update_tokens(cls, refresh_token: str) -> tuple[int, str, str]:
        """Обновляет токены по refresh token."""
        user_id, token_jti = await cls._decode_token(
            refresh_token, require_refresh=True
        )
        # Проверяем что refresh token есть в Redis
        redis = redis_client.get_redis()
        key = f"user:{user_id}:token:{token_jti}"
        if await redis.get(key) is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Сессия истекла."
            )
        # Удаляем старый refresh token
        await redis.delete(key)
        # Создаем новую пару токенов
        access, refresh = await cls.create_tokens(user_id)
        return user_id, access, refresh

    @classmethod
    def verify_password(
        cls,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Проверяет пароль."""
        return _verify_password(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Хеширует пароль."""
        return _get_password_hash(password)

    @classmethod
    async def _decode_token(
        cls, token: str, require_refresh: bool = False
    ) -> tuple[int, str | None]:
        """Декодирует JWT токен."""
        try:
            payload = jwt.decode(
                token, Keys.get_public_key(), algorithms=[ALGORITHM]
            )
            if require_refresh and payload.get("type") != "refresh":
                raise PyJWTError()
            user_id = payload.get("sub")
            if user_id is None:
                raise PyJWTError()
            return int(user_id), payload.get("jti")
        except PyJWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Неверные учетные данные."
            )

    @classmethod
    async def get_current_user(
        cls,
        access: Annotated[
            HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    ) -> int:
        """Извлекает ID текущего пользователя из токена."""
        user_id, _ = await cls._decode_token(access.credentials)
        return user_id
