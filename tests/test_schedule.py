"""
Tests for schedule endpoints: list, get, create, update, delete.
"""
import pytest
import time


class TestGetScheduleEndpoint:
    """Tests for GET /schedule endpoint."""

    def test_get_schedule_empty(self, client, auth_headers):
        """Test getting schedules when none exist."""
        response = client.get("/schedule", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_schedule_with_data(self, client, auth_headers, created_schedule):
        """Test getting schedules after creation."""
        response = client.get("/schedule", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created_schedule["id"]


class TestGetScheduleByIdEndpoint:
    """Tests for GET /schedule/{schedule_id} endpoint."""

    def test_get_schedule_by_id_success(self, client, auth_headers, created_schedule):
        """Test getting a specific schedule."""
        schedule_id = created_schedule["id"]
        response = client.get(f"/schedule/{schedule_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == schedule_id
        assert data["title"] == created_schedule["title"]

    def test_get_schedule_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent schedule."""
        response = client.get("/schedule/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404


class TestCreateScheduleEndpoint:
    """Tests for POST /schedule endpoint."""

    def test_create_schedule_success(self, client, auth_headers, schedule_data):
        """Test creating a new schedule."""
        response = client.post(
            "/schedule",
            headers=auth_headers,
            json=schedule_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == schedule_data["title"]
        assert data["description"] == schedule_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_schedule_unauthorized(self, client, schedule_data):
        """Test creating schedule requires authentication."""
        response = client.post("/schedule", json=schedule_data)
        
        assert response.status_code == 401


class TestUpdateScheduleEndpoint:
    """Tests for PUT /schedule/{schedule_id} endpoint."""

    def test_update_schedule_success(self, client, auth_headers, created_schedule):
        """Test updating an existing schedule."""
        schedule_id = created_schedule["id"]
        updated_data = {
            "title": "Updated Schedule Title",
            "description": "Updated description",
            "start_date": int(time.time()),
            "end_date": int(time.time()) + 7200
        }
        
        response = client.put(
            f"/schedule/{schedule_id}",
            headers=auth_headers,
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == updated_data["title"]
        assert data["description"] == updated_data["description"]

    def test_update_schedule_not_found(self, client, auth_headers, schedule_data):
        """Test updating non-existent schedule."""
        response = client.put(
            "/schedule/nonexistent-id",
            headers=auth_headers,
            json=schedule_data
        )
        
        assert response.status_code == 404


class TestDeleteScheduleEndpoint:
    """Tests for DELETE /schedule/{schedule_id} endpoint."""

    def test_delete_schedule_success(self, client, auth_headers, created_schedule):
        """Test deleting a schedule."""
        schedule_id = created_schedule["id"]
        response = client.delete(f"/schedule/{schedule_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify schedule is no longer accessible
        get_response = client.get(f"/schedule/{schedule_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_schedule_not_found(self, client, auth_headers):
        """Test deleting non-existent schedule."""
        response = client.delete("/schedule/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404
