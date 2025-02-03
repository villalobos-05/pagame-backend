from pydantic import BaseModel, EmailStr, constr


class User(BaseModel):
    id: str
    username: str
    password: str
    email: EmailStr
    createdAt: str  # ISO format
    refreshToken: str | None = None  # uuid


class CreateUser(BaseModel):
    username: constr(min_length=4, max_length=16)  # type: ignore
    email: EmailStr
    password: constr(min_length=8)  # type: ignore


class LogUser(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str
