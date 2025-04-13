from fastapi import APIRouter, Depends, HTTPException, status

from app.security.auth import jwt_security
from app.config.db.conn import execute_query, fetch_one, fetch_paginated
from app.core.schema.base import PaginatedResponse
from app.core.schema.user import UserCreateSchema, UserResponseSchema

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateSchema):
    check_query = "SELECT id FROM users WHERE email = %s"
    existing_user = fetch_one(check_query, (user.email,))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    needed_columns = {
        "first_name",
        "last_name",
        "email",
        "password",
        "phone",
        "dob",
        "gender",
    }
    user_data = user.model_dump(exclude_unset=True)
    missing_columns = needed_columns - user_data.keys()
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing_columns)}",
        )

    gender_value = user.gender.value if hasattr(user.gender, "value") else user.gender
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    hashed_password = jwt_security.get_password_hash(user.password)

    insert_query = """
        INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """

    try:
        created_user = fetch_one(
            insert_query,
            (
                user.first_name,
                user.last_name,
                user.email,
                hashed_password,
                user.phone,
                user.dob,
                gender_value,
                role_value,
            ),
        )
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        ) from e


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
)
def get_user_by_id(
    user_id: int,
    _=Depends(jwt_security.get_current_user),
):
    query = "SELECT * FROM users WHERE id = %s"
    user = fetch_one(query, (user_id,))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("", response_model=PaginatedResponse[UserResponseSchema])
def get_all_users(page: int = 1, page_size: int = 10):
    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and page size must be greater than 0",
        )

    query = "SELECT * FROM users"
    users, total = fetch_paginated(query, page=page, page_size=page_size)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found",
        )
    return {
        "results": users,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/update/{user_id}")
def update_user(
    user_id: int,
    user: UserCreateSchema,
    _=Depends(jwt_security.get_current_user),
):
    check_query = "SELECT id FROM users WHERE id = %s"
    existing_user = fetch_one(check_query, (user_id,))
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    allowed_columns = {
        "first_name",
        "last_name",
        "email",
        "password",
        "phone",
        "dob",
        "gender",
    }
    user_data = user.model_dump(exclude_unset=True)

    if "gender" in user_data and hasattr(user_data["gender"], "value"):
        user_data["gender"] = user_data["gender"].value

    if "password" in user_data and hasattr(user_data["password"], "value"):
        user_data["password"] = jwt_security.get_password_hash(user_data["password"])

    user_data = {
        k: v for k, v in user_data.items() if k in allowed_columns and v is not None
    }
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update.",
        )

    update_fields = [f"{field} = %s" for field in user_data.keys()]
    update_values = list(user_data.values())
    update_values.append(user_id)

    update_query = f"""
        UPDATE users
        SET {", ".join(update_fields)}
        WHERE id = %s
        RETURNING id, first_name, last_name, email, phone, dob, gender, created_at, updated_at
    """

    try:
        updated_user = fetch_one(update_query, tuple(update_values))
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        ) from e


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _=Depends(jwt_security.get_current_user),
):
    check_query = "SELECT id FROM users WHERE id = %s"
    existing_user = fetch_one(check_query, (user_id,))
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_query = "DELETE FROM users WHERE id = %s"
    try:
        execute_query(delete_query, (user_id,))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        ) from e
