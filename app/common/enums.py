from enum import Enum


class GenderEnum(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class GenreEnum(Enum):
    RNB = "RNB"
    COUNTRY = "COUNTRY"
    CLASSIC = "CLASSIC"
    ROCK = "ROCK"
    JAZZ = "JAZZ"


class UserRoleEnum(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
