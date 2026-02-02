from pydantic import BaseModel, Field


class SignInRequestSchema(BaseModel):
    """Модель для авторизации (передаётся через Form)."""
    username: str = Field(max_length=64)
    password: str = Field(max_length=256)
