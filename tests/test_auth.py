"""
Tests for authentication endpoints: /register and /token.
"""
import pytest


class TestRegisterEndpoint:
    """Tests for POST /register endpoint."""

    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "password" not in data  # Password should not be returned
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, registered_user, test_user_data):
        """Test registration fails for duplicate username."""
        response = client.post("/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestTokenEndpoint:
    """Tests for POST /token endpoint."""

    def test_login_success(self, client, registered_user):
        """Test successful login returns access token."""
        response = client.post(
            "/token",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        """Test login fails with wrong password."""
        response = client.post(
            "/token",
            data={
                "username": registered_user["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user."""
        response = client.post(
            "/token",
            data={
                "username": "nonexistent",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
