from fastapi import APIRouter, HTTPException, status

from app.config.db.conn import fetch_one, fetch_paginated, execute_query
from app.core.schema.base import PaginatedResponse
from app.core.schema.music import (
    MusicCreateSchema,
    MusicResponseSchema,
    MusicUpdateSchema,
)

router = APIRouter(prefix="/music", tags=["music"])


@router.get(
    "/artist/{artist_id}", response_model=PaginatedResponse[MusicResponseSchema]
)
def get_music_by_artist(artist_id: int, page: int = 1, page_size: int = 10):
    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and page size must be greater than 0",
        )

    query = "SELECT * FROM music WHERE artist_id = %s"
    music, total = fetch_paginated(query, (artist_id,), page=page, page_size=page_size)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No music found for this artist",
        )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": music,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_music(music: MusicCreateSchema):
    check_query = "SELECT id FROM music WHERE title = %s AND artist_id = %s"
    existing_music = fetch_one(check_query, (music.title, music.artist_id))
    if existing_music:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Music with this title already exists for this artist",
        )

    genre_value = music.genre.value if hasattr(music.genre, "value") else music.genre

    insert_query = """
        INSERT INTO music (artist_id, title, album_name, genre)
        VALUES (%s, %s, %s, %s) RETURNING id
    """

    try:
        created_music = fetch_one(
            insert_query,
            (music.artist_id, music.title, music.album_name, genre_value),
        )
        return created_music
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating music: {str(e)}",
        ) from e


@router.put("/update/{music_id}", status_code=status.HTTP_200_OK)
def update_music(music_id: int, music: MusicUpdateSchema):
    check_query = "SELECT id FROM music WHERE id = %s"
    existing_music = fetch_one(check_query, (music_id,))
    if not existing_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )

    allowed_columns = {
        "title",
        "album_name",
        "genre",
        "artist_id",
    }
    music_data = music.model_dump(exclude_unset=True)

    if "genre" in music_data and hasattr(music_data["genre"], "value"):
        music_data["genre"] = music_data["genre"].value

    music_data = {k: v for k, v in music_data.items() if k in allowed_columns}
    if not music_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update",
        )

    update_fields = [f"{k} = %s" for k in music_data.keys()]
    update_values = list(music_data.values())
    update_values.append(music_id)

    update_query = f"""
        UPDATE music 
        SET {", ".join(update_fields)} 
        WHERE id = %s 
        RETURNING id, title, album_name, genre, artist_id
    """

    try:
        updated_music = fetch_one(update_query, tuple(update_values))
        return updated_music
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating music: {str(e)}",
        ) from e


@router.delete("/delete/{music_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_music(music_id: int):
    check_query = "SELECT id FROM music WHERE id = %s"
    existing_music = fetch_one(check_query, (music_id,))
    if not existing_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found",
        )

    delete_query = "DELETE FROM music WHERE id = %s"

    try:
        execute_query(delete_query, (music_id,))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting music: {str(e)}",
        ) from e
