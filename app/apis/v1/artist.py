from fastapi import APIRouter, HTTPException, status

from app.config.db.conn import execute_query, fetch_paginated, fetch_one
from app.core.schema.artist import (
    ArtistCreateSchema,
    ArtistResponseSchema,
    ArtistUpdateSchema,
)
from app.core.schema.base import PaginatedResponse

router = APIRouter(prefix="/artist", tags=["artist"])


@router.get("/{artist_id}", response_model=ArtistResponseSchema)
def get_artist_by_id(artist_id: int):
    query = "SELECT * FROM artists WHERE id = %s"
    artist = fetch_one(query, (artist_id,))
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )
    return artist


@router.get("/", response_model=PaginatedResponse[ArtistResponseSchema])
def get_artists(page: int = 1, page_size: int = 10):
    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and page size must be greater than 0",
        )

    query = "SELECT * FROM artists"
    artists, total = fetch_paginated(query, page=page, page_size=page_size)
    if not artists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No artists found",
        )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": artists,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_artist(artist: ArtistCreateSchema):
    check_query = "SELECT id FROM artists WHERE name = %s"
    existing_artist = fetch_one(check_query, (artist.name,))
    if existing_artist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artist with this name already exists",
        )

    insert_query = """
        INSERT INTO artists (name, dob, address, first_release_year, no_of_albums_released)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """

    try:
        created_artist = fetch_one(
            insert_query,
            (
                artist.name,
                artist.dob,
                artist.address,
                artist.first_release_year,
                artist.no_of_albums_released,
            ),
        )
        return {
            "message": "Artist created successfully",
            "artist_id": created_artist["id"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating artist: {str(e)}",
        ) from e


@router.put(
    "/{artist_id}",
)
def update_artist(artist_id: int, artist: ArtistUpdateSchema):
    check_query = "SELECT id FROM artists WHERE id = %s"
    existing_artist = fetch_one(check_query, (artist_id,))
    if not existing_artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    allowed_columns = {
        "name",
        "dob",
        "address",
        "first_release_year",
        "no_of_albums_released",
    }
    artist_data = artist.model_dump(exclude_unset=True)
    artist_data = {k: v for k, v in artist_data.items() if k in allowed_columns}
    if not artist_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update",
        )

    update_fields = [f"{field} = %s" for field in artist_data.keys()]
    update_values = list(artist_data.values())
    update_values.append(artist_id)

    update_query = f"""
        UPDATE artists
        SET {", ".join(update_fields)}
        WHERE id = %s
        RETURNING id, name, dob, address, first_release_year, no_of_albums_released
    """

    try:
        updated_user = fetch_one(update_query, tuple(update_values))
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating artist: {str(e)}",
        ) from e


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(artist_id: int):
    check_query = "SELECT id FROM artists WHERE id = %s"
    existing_artist = fetch_one(check_query, (artist_id,))
    if not existing_artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found",
        )

    delete_query = "DELETE FROM artists WHERE id = %s"
    try:
        execute_query(delete_query, (artist_id,))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting artist: {str(e)}",
        ) from e
