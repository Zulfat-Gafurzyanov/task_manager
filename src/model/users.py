from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Базовая модель пользователя (без чувствительных полей)."""
    id: int = Field(gt=0)
    username: str = Field(min_length=3, max_length=64)
    role: str = Field(max_length=32)

    model_config = ConfigDict(from_attributes=True)
