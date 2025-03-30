import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_user():
    return {
        "id": 1,
        "first_name": "Ram",
        "last_name": "Thapa",
        "email": "ram.thapa@example.com",
        "password": "password123",
        "phone": "1234567890",
        "dob": "1990-01-01",
        "gender": "male",
        "created_at": "2025-03-30T12:00:00",
        "updated_at": "2025-03-30T12:00:00",
    }


@pytest.fixture
def mock_users_list():
    return [
        {
            "id": 1,
            "first_name": "Ram",
            "last_name": "Thapa",
            "email": "ram.thapa@example.com",
            "password": "password123",
            "phone": "1234567890",
            "dob": "1990-01-01",
            "gender": "male",
            "created_at": "2025-03-30T12:00:00",
            "updated_at": "2025-03-30T12:00:00",
        },
        {
            "id": 2,
            "first_name": "Alice",
            "last_name": "Jane",
            "email": "alice.jane@example.com",
            "password": "password456",
            "phone": "0987654321",
            "dob": "1992-02-02",
            "gender": "female",
            "created_at": "2025-03-30T12:00:00",
            "updated_at": "2025-03-30T12:00:00",
        },
    ]


class TestUserAPI:
    @patch("app.apis.v1.user.fetch_one")
    def test_create_user_success(self, mock_fetch_one, mock_user):
        mock_fetch_one.side_effect = [None, {"id": 1}]

        new_user = {
            "first_name": "Ram",
            "last_name": "Thapa",
            "email": "ram.thapa@example.com",
            "password": "password123",
        }

        response = client.post("api/v1/user/create", json=new_user)

        assert response.status_code == 201
        assert response.json() == {"id": 1}

        mock_fetch_one.assert_any_call(
            "SELECT id FROM users WHERE email = %s",
            (new_user["first_name"], new_user["email"]),
        )
        mock_fetch_one.assert_any_call(
            """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%s, %s, %s, %s) RETURNING id
    """,
            (
                new_user["first_name"],
                new_user["last_name"],
                new_user["email"],
                new_user["password"],
            ),
        )

    @patch("app.apis.v1.user.fetch_one")
    def test_create_user_already_exists(self, mock_fetch_one):
        mock_fetch_one.return_value = {"id": 1}

        new_user = {
            "first_name": "Ram",
            "last_name": "Thapa",
            "email": "ram.thapa@example.com",
            "password": "password123",
        }

        response = client.post("api/v1/user/create", json=new_user)

        assert response.status_code == 400
        assert response.json() == {"detail": "User with this email already exists"}

    @patch("app.apis.v1.user.fetch_one")
    def test_create_user_error(self, mock_fetch_one):
        mock_fetch_one.side_effect = [None, Exception("Database error")]

        new_user = {
            "first_name": "Ram",
            "last_name": "Thapa",
            "email": "ram.thapa@example.com",
            "password": "password123",
        }

        response = client.post("api/v1/user/create", json=new_user)

        assert response.status_code == 500
        assert "Error creating user" in response.json()["detail"]

    @patch("app.apis.v1.user.fetch_one")
    def test_get_user_by_id_success(self, mock_fetch_one, mock_user):
        mock_fetch_one.return_value = mock_user

        response = client.get("api/v1/user/1")

        assert response.status_code == 200
        assert response.json() == mock_user
        mock_fetch_one.assert_called_once_with(
            "SELECT * FROM users WHERE id = %s", (1,)
        )

    @patch("app.apis.v1.user.fetch_one")
    def test_get_user_by_id_not_found(self, mock_fetch_one):
        mock_fetch_one.return_value = None

        response = client.get("api/v1/user/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    # Test get_all_users endpoint
    @patch("app.apis.v1.user.fetch_paginated")
    def test_get_all_users_success(self, mock_fetch_paginated, mock_users_list):
        mock_fetch_paginated.return_value = (mock_users_list, 2)

        response = client.get("api/v1/user")

        assert response.status_code == 200
        assert response.json() == {
            "results": mock_users_list,
            "total": 2,
            "page": 1,
            "page_size": 10,
        }
        mock_fetch_paginated.assert_called_once_with(
            "SELECT * FROM users", page=1, page_size=10
        )

    @patch("app.apis.v1.user.fetch_paginated")
    def test_get_all_users_not_found(self, mock_fetch_paginated):
        mock_fetch_paginated.return_value = ([], 0)

        response = client.get("api/v1/user")

        assert response.status_code == 404
        assert response.json() == {"detail": "No users found"}

    def test_get_all_users_invalid_pagination(self):
        response = client.get("api/v1/user/?page=0&page_size=0")

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Page and page size must be greater than 0"
        }

    @patch("app.apis.v1.user.fetch_one")
    def test_update_user_success(self, mock_fetch_one, mock_user):
        mock_fetch_one.side_effect = [{"id": 1}, mock_user]

        update_data = {
            "first_name": "Ram",
            "last_name": "Updated",
            "email": "ram.updated@example.com",
        }

        response = client.put("api/v1/user/update/1", json=update_data)

        assert response.status_code == 200
        assert response.json() == mock_user

    @patch("app.apis.v1.user.fetch_one")
    def test_update_user_not_found(self, mock_fetch_one):
        mock_fetch_one.return_value = None

        update_data = {"first_name": "Ram", "last_name": "Updated"}

        response = client.put("api/v1/user/update/999", json=update_data)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    @patch("app.apis.v1.user.fetch_one")
    def test_update_user_no_fields(self, mock_fetch_one):
        mock_fetch_one.return_value = {"id": 1}

        update_data = {}

        response = client.put("api/v1/user/update/1", json=update_data)

        assert response.status_code == 400
        assert response.json() == {"detail": "No valid fields provided for update."}

    @patch("app.apis.v1.user.fetch_one")
    def test_update_user_error(self, mock_fetch_one):
        mock_fetch_one.side_effect = [{"id": 1}, Exception("Database error")]

        update_data = {"first_name": "Ram", "last_name": "Updated"}

        response = client.put("api/v1/user/update/1", json=update_data)

        assert response.status_code == 500
        assert "Error updating user" in response.json()["detail"]

    @patch("app.apis.v1.user.fetch_one")
    @patch("app.apis.v1.user.execute_query")
    def test_delete_user_success(self, mock_execute_query, mock_fetch_one):
        mock_fetch_one.return_value = {"id": 1}

        response = client.delete("api/v1/user/delete/1")

        assert response.status_code == 204
        mock_fetch_one.assert_called_once_with(
            "SELECT id FROM users WHERE id = %s", (1,)
        )
        mock_execute_query.assert_called_once_with(
            "DELETE FROM users WHERE id = %s", (1,)
        )

    @patch("app.apis.v1.user.fetch_one")
    def test_delete_user_not_found(self, mock_fetch_one):
        mock_fetch_one.return_value = None

        response = client.delete("api/v1/user/delete/999")

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    @patch("app.apis.v1.user.fetch_one")
    @patch("app.apis.v1.user.execute_query")
    def test_delete_user_error(self, mock_execute_query, mock_fetch_one):
        mock_fetch_one.return_value = {"id": 1}
        mock_execute_query.side_effect = Exception("Database error")

        response = client.delete("api/v1/user/delete/1")

        assert response.status_code == 500
        assert "Error deleting user" in response.json()["detail"]
