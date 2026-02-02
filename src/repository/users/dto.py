from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    """DTO для создания пользователя."""
    username: str
    password: str
    email: str
    phone: str
    rules: list[str]


class UserResponseDTO(BaseModel):
    """DTO для возврата пользователя (без чувствительных полей)."""
    id: int
    username: str


class UserWithEmailDTO(BaseModel):
    """DTO для возврата пользователя с email."""
    id: int
    username: str
    email: str


class UserWithPasswordAndEmailDTO(BaseModel):
    """DTO для внутренней проверки пароля (содержит хеш)."""
    id: int
    username: str
    email: str
    password: str


class UserWithUUIDDTO(BaseModel):
    """DTO для возврата пользователя с UUID."""
    id: int
    username: str
    uuid: str


class RuleDTO(BaseModel):
    """DTO для одной роли."""
    name: str


class UserRulesDTO(BaseModel):
    """DTO для списка ролей пользователя."""
    rules: list[RuleDTO]
