from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from passlib.context import CryptContext
from app.common.exceptions import InvalidCredentialsException, UserNotFoundException
from app.config import settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.config.db.conn import fetch_one


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class JWTSecurity(object):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_TIME_IN_MINUTES = settings.REFRESH_TOKEN_TIME_IN_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def get_user(self, email: str):
        query = "SELECT * FROM users WHERE email = %s"
        user = fetch_one(query, (email,))
        return user

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            email = self.decode_access_token_and_return_email(token)
            if email is None:
                raise InvalidCredentialsException("Invalid credentials")
        except JWTError:
            raise InvalidCredentialsException("Invalid credentials")

        user = self.get_user(email=email)
        if not user:
            raise UserNotFoundException("User not found")
        return user

    def authenticate_user(self, email: str, password: str):
        user = self.get_user(email)
        if not user:
            raise UserNotFoundException("User not found")
        if not self.verify_password(password, user["password"]):
            raise InvalidCredentialsException("Invalid credentials")
        return user

    def create_access_token(self, data: dict, expires_delta=None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=300)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        to_encode.update({"token": "refresh"})
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=43200)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def validate_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("email")
            if email is None:
                raise InvalidCredentialsException("Invalid credentials")
        except JWTError:
            raise InvalidCredentialsException("Invalid credentials")

        try:
            refresh_token = payload.get("token")
            if not refresh_token:
                raise InvalidCredentialsException("Invalid credentials")
        except JWTError:
            raise InvalidCredentialsException("Invalid credentials")
        user = self.get_user(email=email)
        if not user:
            raise UserNotFoundException("User not found")
        return user

    def decode_access_token_and_return_email(self, token: str):
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        email: Optional[str] = payload.get("email")
        return email


jwt_security = JWTSecurity()
