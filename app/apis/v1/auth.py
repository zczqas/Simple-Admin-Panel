from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.apis.v1.user import create_user
from app.common.exceptions import InvalidCredentialsException, UserNotFoundException
from app.core.schema.auth import LoginResponseWithToken
from app.core.schema.user import UserCreateSchema
from app.security.auth import jwt_security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponseWithToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = jwt_security.authenticate_user(form_data.username, form_data.password)
    except (UserNotFoundException, InvalidCredentialsException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    basic_user_info = {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "role": user["role"],
    }

    return LoginResponseWithToken(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"],
        role=user["role"],
        token_type="bearer",
        access_token=jwt_security.create_access_token(data=basic_user_info),
        refresh_token=jwt_security.create_refresh_token(data=basic_user_info),
    )


@router.post("/register")
async def register(user: UserCreateSchema):
    try:
        create_user(user=user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return {"message": "User registered successfully"}


@router.post("/refresh-token")
async def refresh_access_token(refresh_token: str):
    user = jwt_security.validate_refresh_token(refresh_token)
    data = {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "role": user["role"],
    }

    return {
        "access_token": jwt_security.create_access_token(data=data),
        "refresh_token": jwt_security.create_refresh_token(data=data),
    }
