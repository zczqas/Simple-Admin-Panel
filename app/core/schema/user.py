from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from app.common.enums import GenderEnum, UserRoleEnum


class UserBaseSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    role: Optional[UserRoleEnum] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserResponseSchema(UserBaseSchema):
    id: int


class UserCreateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    role: Optional[UserRoleEnum] = None
