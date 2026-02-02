import datetime as dt
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

# from databases.users import crud as users_crud
from src.constants.tokens import ACCESS_TOKEN_EXPIRE, ALGORITHM, REFRESH_TOKEN_EXPIRE
# from src.core.connections_storage import ConnectionsStorage
from src.core.encryption import Encryption
from src.core.keys import Keys
from src.db.redis import redis_client
from src.model.requests.users_requests import SignInRequestSchema
from src.model.tokens import RulesSchema
from src.model.users import UserBaseSchema, UserBaseWithEmail, UserBaseWithPasswordAndEmail, UserBaseWithUUIDSchema
from src.repository.users.dto import UserCreateDTO
from src.repository.users.users import UserRepository

bearer_scheme = HTTPBearer()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! убрать работу с DTO юзера в сервисный слой!
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=131072,
    argon2__parallelism=4,
    argon2__time_cost=3,
)


def _get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class Security:
    """Класс для работы с авторизацией и аутентификацией."""

    @staticmethod
    async def _create_token(
        user_id: int, 
        token_type: str, 
        token_expire: int, 
        scopes: list[str],
    ) -> str:
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
        
        token = jwt.encode(payload, Keys.get_private_key(), algorithm=ALGORITHM)
        
        # Refresh-токен сохраняем в Redis для возможности отзыва.
        if token_type == "refresh":
            redis = redis_client.get_redis()
            ttl = int(dt.timedelta(hours=token_expire).total_seconds())
            await redis.setex(
                f"user:{user_id}:token:{jti}", ttl, token
            )

        return token

    @classmethod
    async def create_tokens(cls, user_id: int) -> tuple[str, str, RulesSchema]:
        """Создаёт пару access + refresh токенов для пользователя."""
        user_rules_dto = await user_repo.get_available_rules_for_user(user_id=user_id)
        scope_names = [rule.name for rule in user_rules_dto.rules]
        user_scopes = RulesSchema.model_validate(user_rules_dto)  # DTO -> Pydantic-модель.
        
        access_token = await cls._create_token(
            user_id, "access", ACCESS_TOKEN_EXPIRE, scope_names
        )
        refresh_token = await cls._create_token(
            user_id, "refresh", REFRESH_TOKEN_EXPIRE, scope_names
        )
        
        return access_token, refresh_token, user_scopes
    
 @classmethod
    async def update_tokens(
        cls, refresh_token: str, user_repo: UserRepository
    ) -> tuple[int, str, str, RulesSchema]:
        """Обновляет токены по валидному refresh-токену."""
        user_id, _, token_jti = await cls._decode_token(refresh_token, require_refresh=True)
        
        redis = redis_client.get_redis()
        key = f"user:{user_id}:token:{token_jti}"
        if await redis.get(key) is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Сессия истекла.")
        
        await redis.delete(key)  # Удаляем использованный refresh-токен
        access, refresh, scopes = await cls.create_tokens(user_id, user_repo)
        return user_id, access, refresh, scopes

    @classmethod
    async def authenticate_user(
        cls, form_data: Annotated[SignInRequestSchema, Form()]
    ) -> UserBaseWithEmail:
        """Проверяет логин и пароль, возвращает пользователя."""
        user_dto = await user_repo.get_user_by_login(form_data.username)
        user = UserBaseWithPasswordAndEmail.model_validate(user_dto)  # DTO -> Pydantic-модель.
        
        if not _verify_password(form_data.password, user.password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверный логин или пароль.")
        
        return UserBaseWithEmail(id=user.id, username=user.username, email=user.email)

    @classmethod
    async def _decode_token(
        cls, token: str, require_refresh: bool = False
    ) -> tuple[int, list[str], str | None]:
        """Декодирует и валидирует JWT-токен."""
        try:
            payload = jwt.decode(token, Keys.get_public_key(), algorithms=[ALGORITHM])
            
            if require_refresh and payload.get("type") != "refresh":
                raise PyJWTError()
            
            user_id = payload.get("sub")
            if user_id is None:
                raise PyJWTError()
                
            return int(user_id), payload.get("scopes", []), payload.get("jti")
            
        except PyJWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверные учетные данные.") from None

    @staticmethod
    async def _check_scopes(security_scopes: SecurityScopes, token_scopes: list[str], user_id: int, user_repo: UserRepository) -> None:
        """Проверяет наличие нужных scopes. Если в токене нет — перепроверяет БД."""
        if not security_scopes.scopes:
            return
            
        missing = set(security_scopes.scopes) - set(token_scopes)
        if not missing:
            return
        
        # Проверяем актуальные права в БД
        db_rules = await user_repo.get_available_rules_for_user(user_id=user_id)
        db_scopes = {rule.name for rule in db_rules.rules}
        
        if missing - db_scopes:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав.")

    @classmethod
    async def get_current_user(
        cls,
        access: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
        security_scopes: SecurityScopes,
        user_repo: UserRepository,
    ) -> UserBaseSchema:
        """Dependency: извлекает текущего пользователя из access-токена."""
        user_id, token_scopes, _ = await cls._decode_token(access.credentials)
        await cls._check_scopes(security_scopes, token_scopes, user_id, user_repo)

        user_dto = await user_repo.get_user_by_user_id(user_id)
        return UserBaseSchema.model_validate(user_dto)

    @classmethod
    async def get_current_user_with_uuid(
        cls,
        access: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
        security_scopes: SecurityScopes,
        user_repo: UserRepository,
    ) -> UserBaseWithUUIDSchema:
        """Dependency: извлекает текущего пользователя с UUID из access-токена."""
        user_id, token_scopes, _ = await cls._decode_token(access.credentials)
        await cls._check_scopes(security_scopes, token_scopes, user_id, user_repo)

        user_dto = await user_repo.get_user_with_uuid_by_user_id(user_id)
        return UserBaseWithUUIDSchema.model_validate(user_dto)

    @classmethod
    async def create_user(
        cls, 
        username: str, 
        password: str, 
        email: str, 
        phone: str, 
        rules: list[str],
    ) -> UserBaseSchema:
        """Создаёт пользователя с хешем пароля и зашифрованными email/phone."""
        hashed_password = _get_password_hash(password)
        encrypted_email = await Encryption.encrypt_value(email)
        encrypted_phone = await Encryption.encrypt_value(phone)
        
        data = UserCreateDTO(
            username=username,
            password=hashed_password,
            email=encrypted_email,
            phone=encrypted_phone,
            rules=rules,
        )
        user_dto = await user_repo.create_user_with_rules(data)

        return UserBaseSchema.model_validate(user_dto)

 @classmethod
    async def update_user_password(cls, user_id: int, new_password: str) -> None:
        """Обновляет пароль пользователя."""
        hashed_password = _get_password_hash(new_password)
        await user_repo.update_user_password_by_user_id(user_id, hashed_password)
