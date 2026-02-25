from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    """DTO для создания пользователя."""
    username: str
    password: str
    email: str
    phone: str
    role: str = "user"


class UserResponseDTO(BaseModel):
    """DTO для возврата пользователя (без чувствительных полей)."""
    id: int
    username: str
    role: str


class UserWithEmailAndPasswordDTO(BaseModel):
    """DTO для внутренней проверки пароля (содержит хеш)."""
    id: int
    username: str
    email: str
    hashed_password: str
    role: str
