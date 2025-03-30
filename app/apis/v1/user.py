from fastapi import APIRouter, HTTPException, status

from app.config.db.conn import execute_query, fetch_one, fetch_paginated
from app.core.schema.user import UserCreateSchema, UserResponseSchema

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create")
async def create_user(user: UserCreateSchema):
    check_query = "SELECT id FROM users WHERE first_name = %s OR email = %s"
    existing_user = fetch_one(check_query, (user.first_name, user.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name or email already exists",
        )

    insert_query = """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%s, %s, %s, %s) RETURNING id
    """

    created_user = fetch_one(
        insert_query,
        (user.first_name, user.last_name, user.email, user.password),
    )
    return created_user


@router.get("/{user_id}")
def get_user_by_id(user_id: int):
    query = "SELECT * FROM users WHERE id = %s"
    user = fetch_one(query, (user_id,))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/")
def get_all_users(page: int = 1, page_size: int = 10):
    query = "SELECT * FROM users"
    users = fetch_paginated(query, page=page, page_size=page_size)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found",
        )
    return users


@router.put("/update/{user_id}")
def update_user(user_id: int, user: UserCreateSchema):
    check_query = "SELECT id FROM users WHERE id = %s"
    existing_user = fetch_one(check_query, (user_id,))
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_query = """
        UPDATE users
        SET first_name = %s, last_name = %s, email = %s, password = %s
        WHERE id = %s
    """
    updated_user = fetch_one(
        update_query,
        (user.first_name, user.last_name, user.email, user.password, user_id),
    )
    return updated_user


@router.delete("/delete/{user_id}")
def delete_user(user_id: int):
    check_query = "SELECT id FROM users WHERE id = %s"
    existing_user = fetch_one(check_query, (user_id,))
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_query = "DELETE FROM users WHERE id = %s"
    execute_query(delete_query, (user_id,))

    return {"detail": "User deleted successfully"}
