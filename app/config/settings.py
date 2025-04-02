import os

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

env = os.environ.get("APP_ENV", "DEV")

if env == "PROD":
    config = Config(".env-prod")
else:
    config = Config(".env")


VERSION: str = config("VERSION", default="1.0.0")
DEBUG: bool = config("DEBUG", cast=bool, default=False)
APP_ENV: str = config("APP_ENV", default="DEVELOPMENT")
PROJECT_NAME: str = config("PROJECT_NAME", default="artist_management")
PROJECT_DESCRIPTION: str = config(
    "PROJECT_DESCRIPTION", default="Artist Management API"
)

ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="*"
)
SECRET_KEY: Secret = config("SECRET_KEY", default="secret")
ALGORITHM: str = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=300)
REFRESH_TOKEN_TIME_IN_MINUTES: int = config(
    "REFRESH_TOKEN_TIME_IN_MINUTES", default=43200
)
