from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from src.core.security import Security
from src.dependency.dependencies import get_user_service
from src.model.users import TokenResponse, UserBase, UserCreate, UserLogin
from src.service.users import UserService

router_auth = APIRouter()


@router_auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserBase
)
async def register(
    data: Annotated[UserCreate, Body()],
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserBase:
    """Регистрация нового пользователя."""
    return await service.register_user(data)


@router_auth.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
async def login(
    data: Annotated[UserLogin, Body()],
    service: Annotated[UserService, Depends(get_user_service)]
) -> TokenResponse:
    """Вход в систему."""
    return await service.login_user(data)


@router_auth.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
async def refresh_tokens(
    refresh_token: Annotated[str, Body(embed=True)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> TokenResponse:
    """Обновление токенов."""
    return await service.refresh_tokens(refresh_token)


@router_auth.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserBase
)
async def get_me(
    current_user_id: Annotated[int, Depends(Security.get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserBase:
    """Получить информацию о текущем пользователе."""
    return await service.get_user_by_id(current_user_id)
