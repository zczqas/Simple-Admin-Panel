from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.common.enums import GenderEnum


class ArtistBaseSchema(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    first_release_year: Optional[str] = None
    no_of_albums_released: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArtistCreateSchema(BaseModel):
    name: str
    dob: date
    address: str
    first_release_year: str
    no_of_albums_released: int


class ArtistResponseSchema(ArtistBaseSchema):
    id: int

    class config:
        orm_mode = True


class ArtistUpdateSchema(ArtistBaseSchema):
    pass
