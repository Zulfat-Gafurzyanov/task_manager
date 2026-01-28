from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    id: int
    username: str = Field(min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class UserWithPassword(UserBase):
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
