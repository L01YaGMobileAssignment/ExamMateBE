"""
Tests for the health check endpoint.
"""


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check_returns_up(self, client):
        """Test that health endpoint returns status up."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "up"}
