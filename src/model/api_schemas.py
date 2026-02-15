from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Ответ с токенами доступа."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена."""
    refresh_token: str


class SignUpRequest(BaseModel):
    """Схема для регистрации нового пользователя."""
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)


class SignInRequest(BaseModel):
    """Схема для входа в систему (передаётся через Form)."""
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)
