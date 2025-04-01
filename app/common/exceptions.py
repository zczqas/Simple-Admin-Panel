from fastapi import HTTPException, status


class BaseException(HTTPException):
    """Base exception class for all custom exceptions."""

    def __init__(self, status_code: int, detail: str, headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserNotFoundException(BaseException):
    """Exception raised when a user is not found."""

    def __init__(self, message: str):
        detail = message or "User not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidCredentialsException(BaseException):
    """Exception raised for invalid credentials."""

    def __init__(self, message: str):
        detail = message or "Invalid credentials"
        headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )
