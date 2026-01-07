"""
Tests for quiz endpoints: list, search, get, generate, delete.
"""
import json
import pytest
from unittest.mock import patch


class TestGetQuizzesEndpoint:
    """Tests for GET /quizzes endpoint."""

    def test_get_quizzes_empty(self, client, auth_headers):
        """Test getting quizzes when none exist."""
        response = client.get("/quizzes", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_quizzes_with_data(self, client, auth_headers, created_quiz):
        """Test getting quizzes after creation."""
        response = client.get("/quizzes", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["quiz_id"] == created_quiz["quiz_id"]


class TestSearchQuizzesEndpoint:
    """Tests for GET /quizzes/search endpoint."""

    def test_search_quizzes_found(self, client, auth_headers, created_quiz):
        """Test searching for existing quiz."""
        response = client.get(
            "/quizzes/search",
            headers=auth_headers,
            params={"q": "Test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_search_quizzes_not_found(self, client, auth_headers, created_quiz):
        """Test searching for non-existent quiz."""
        response = client.get(
            "/quizzes/search",
            headers=auth_headers,
            params={"q": "nonexistent_xyz_123"}
        )
        
        assert response.status_code == 200
        assert response.json() == []


class TestGetQuizEndpoint:
    """Tests for GET /quizzes/{quiz_id} endpoint."""

    def test_get_quiz_success(self, client, auth_headers, created_quiz):
        """Test getting a specific quiz with questions."""
        quiz_id = created_quiz["quiz_id"]
        response = client.get(f"/quizzes/{quiz_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quiz_id"] == quiz_id
        assert "questions" in data
        assert len(data["questions"]) >= 1

    def test_get_quiz_not_found(self, client, auth_headers):
        """Test getting non-existent quiz."""
        response = client.get("/quizzes/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404


class TestGenerateQuizEndpoint:
    """Tests for POST /quizzes/generate endpoint."""

    def test_generate_quiz_success(self, client, auth_headers, uploaded_document, tmp_path, mock_llm_response):
        """Test generating quiz with mocked LLM."""
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.quizzes.generate_content") as mock_generate:
                mock_generate.return_value = json.dumps(mock_llm_response)
                
                response = client.post(
                    "/quizzes/generate",
                    headers=auth_headers,
                    json={
                        "document_id": uploaded_document["id"],
                        "num_questions": 1
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "quiz_id" in data
        assert data["quiz_title"] == "Test Quiz"
        assert len(data["questions"]) == 1

    def test_generate_quiz_document_not_found(self, client, auth_headers):
        """Test quiz generation fails for non-existent document."""
        response = client.post(
            "/quizzes/generate",
            headers=auth_headers,
            json={
                "document_id": "nonexistent-doc-id",
                "num_questions": 5
            }
        )
        
        assert response.status_code == 404


class TestDeleteQuizEndpoint:
    """Tests for DELETE /quizzes/{quiz_id} endpoint."""

    def test_delete_quiz_success(self, client, auth_headers, created_quiz):
        """Test deleting a quiz."""
        quiz_id = created_quiz["quiz_id"]
        response = client.delete(f"/quizzes/{quiz_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify quiz is no longer accessible
        get_response = client.get(f"/quizzes/{quiz_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_quiz_not_found(self, client, auth_headers):
        """Test deleting non-existent quiz."""
        response = client.delete("/quizzes/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404
