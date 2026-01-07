"""
Tests for user endpoints: /users/me/ and /users/me/language.
"""
import pytest


class TestGetCurrentUserEndpoint:
    """Tests for GET /users/me/ endpoint."""

    def test_get_current_user_success(self, client, auth_headers, registered_user):
        """Test getting current user information."""
        response = client.get("/users/me/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]

    def test_get_current_user_unauthorized(self, client):
        """Test endpoint requires authentication."""
        response = client.get("/users/me/")
        
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test endpoint rejects invalid token."""
        response = client.get(
            "/users/me/",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401


class TestUpdateUserLanguageEndpoint:
    """Tests for PUT /users/me/language endpoint."""

    def test_update_language_success(self, client, auth_headers):
        """Test updating user language to Vietnamese."""
        response = client.put(
            "/users/me/language",
            headers=auth_headers,
            params={"language": "vi"}
        )
        
        assert response.status_code == 200
        assert "updated" in response.json()["message"].lower()

    def test_update_language_invalid(self, client, auth_headers):
        """Test updating to unsupported language fails."""
        response = client.put(
            "/users/me/language",
            headers=auth_headers,
            params={"language": "fr"}  # French not supported
        )
        
        assert response.status_code == 400
        assert "Invalid language" in response.json()["detail"]

    def test_update_language_unauthorized(self, client):
        """Test endpoint requires authentication."""
        response = client.put(
            "/users/me/language",
            params={"language": "en"}
        )
        
        assert response.status_code == 401
