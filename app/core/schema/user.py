from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBaseSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserResponseSchema(UserBaseSchema):
    pass


class UserCreateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
