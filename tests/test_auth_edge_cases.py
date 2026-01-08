"""
Tests for authentication edge cases in deps.py and security.py.
"""
import pytest
import jwt
from unittest.mock import patch
from datetime import timedelta
from app.core import config


class TestTokenValidationEdgeCases:
    """Test edge cases in token validation (deps.py)."""

    def test_token_without_username_claim(self, client, registered_user):
        """Test token validation fails when username claim is missing."""
        # Create a token without 'sub' claim
        malformed_token = jwt.encode(
            {"some_other_claim": "value"},
            config.SECRET_KEY,
            algorithm=config.ALGORITHM
        )
        
        # Try to access protected endpoint
        response = client.get(
            "/documents",
            headers={"Authorization": f"Bearer {malformed_token}"}
        )
        
        # Should return 401 unauthorized (deps.py line 23)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_token_for_deleted_user(self, client, registered_user, auth_token, setup_test_db):
        """Test token validation fails when user is deleted from database."""
        # Delete user from database after token is issued
        cursor = setup_test_db.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (registered_user["username"],))
        setup_test_db.commit()
        
        # Try to access protected endpoint with old token
        response = client.get(
            "/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return 401 unauthorized (deps.py line 29)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_disabled_user_access(self, client, registered_user, auth_token, setup_test_db):
        """Test that disabled users cannot access protected endpoints."""
        # Disable the user
        cursor = setup_test_db.cursor()
        cursor.execute(
            "UPDATE users SET disabled = ? WHERE username = ?",
            (True, registered_user["username"])
        )
        setup_test_db.commit()
        
        # Try to access protected endpoint
        response = client.get(
            "/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return 400 bad request (deps.py line 36)
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]


class TestTokenExpiryEdgeCases:
    """Test edge cases in token creation (security.py)."""

    def test_default_token_expiry(self):
        """Test that tokens get default 15-minute expiry when no timedelta specified."""
        from app.core.security import create_access_token
        from datetime import datetime, timezone
        
        # Create token without expires_delta
        token = create_access_token(data={"sub": "testuser"}, expires_delta=None)
        
        # Decode token to check expiry
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        # Should have expiry set (security.py line 19)
        assert "exp" in payload
        
        # Expiry should be approximately 15 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = (exp_time - now).total_seconds()
        
        # Allow 5 second tolerance for test execution time
        assert 14 * 60 < time_diff < 16 * 60, f"Expected ~15 min expiry, got {time_diff/60:.1f} min"

    def test_custom_token_expiry(self):
        """Test that custom expiry is used when provided."""
        from app.core.security import create_access_token
        from datetime import datetime, timezone
        
        # Create token with custom expiry
        custom_expiry = timedelta(hours=2)
        token = create_access_token(data={"sub": "testuser"}, expires_delta=custom_expiry)
        
        # Decode token to check expiry
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        # Expiry should be approximately 2 hours from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = (exp_time - now).total_seconds()
        
        # Allow 5 second tolerance
        assert 2 * 60 * 60 - 5 < time_diff < 2 * 60 * 60 + 5
