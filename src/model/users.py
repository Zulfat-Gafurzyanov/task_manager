from pydantic import BaseModel, ConfigDict


class UserBaseSchema(BaseModel):
    """Базовая модель пользователя (без чувствительных полей)."""
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserBaseWithEmail(BaseModel):
    """Модель пользователя с email."""
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserBaseWithPasswordAndEmail(BaseModel):
    """
    Модель пользователя с email и хешем пароля
    (для внутреннего использования).
    """
    id: int
    username: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserBaseWithUUIDSchema(BaseModel):
    """Модель пользователя с UUID."""
    id: int
    username: str
    uuid: str

    model_config = ConfigDict(from_attributes=True)
