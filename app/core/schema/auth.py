from pydantic import BaseModel, EmailStr

from app.common.enums import UserRoleEnum


class LoginResponseWithToken(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRoleEnum
    token_type: str
    access_token: str
    refresh_token: str
