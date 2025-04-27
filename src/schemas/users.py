from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from src.database.models import UserRole


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole


class UserUpdate(BaseModel):
    password: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    password: str
    token: str
