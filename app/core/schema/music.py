from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.common.enums import GenreEnum


class MusicBaseSchema(BaseModel):
    artist_id: Optional[int] = None
    title: Optional[str] = None
    album_name: Optional[str] = None
    genre: Optional[GenreEnum] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MusicCreateSchema(BaseModel):
    artist_id: int
    title: str
    album_name: str
    genre: GenreEnum

    class Config:
        orm_mode = True


class MusicResponseSchema(MusicBaseSchema):
    id: int

    class Config:
        orm_mode = True


class MusicUpdateSchema(MusicBaseSchema):
    pass
