from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    username: str
    hashed_password: str


class UserDTO(BaseModel):
    id: int
    username: str


class UserWithPasswordDTO(BaseModel):
    id: int
    username: str
    password: str
