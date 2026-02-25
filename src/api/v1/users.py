from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, status

from src.api.v1.dependencies import (
    get_cache_repository,
    get_user_repository,
    get_user_service,
)
from src.core.security import Security
from src.model.api_schemas import (
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse
)
from src.model.users import UserBase
from src.repository.cache import CacheRepository
from src.repository.users.users import UserRepository
from src.service.users import UserService

router_v1 = APIRouter()


@router_v1.post(
    "/signup",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def signup(
    data: Annotated[SignUpRequest, Body()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.register(data)


@router_v1.post(
    "/signin",
    response_model=TokenResponse,
    summary="Вход в систему"
)
async def signin(
    form_data: Annotated[SignInRequest, Form()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)],
):
    return await Security.sign_in(form_data, user_repo, cache_repo)


@router_v1.post(
    "/signout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы"
)
async def signout(
    current_user: Annotated[UserBase, Depends(Security.get_current_user)],
    cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)],
):
    await Security.signout(current_user.id, cache_repo)


@router_v1.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновление токенов"
)
async def refresh_tokens(
    data: Annotated[RefreshTokenRequest, Body()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)],
):
    return await Security.refresh_tokens(
        data.refresh_token, user_repo, cache_repo)


@router_v1.get(
    "/me",
    response_model=UserBase,
    summary="Получить информацию о текущем пользователе"
)
async def get_me(
    current_user: Annotated[UserBase, Depends(Security.get_current_user)],
):
    return current_user
