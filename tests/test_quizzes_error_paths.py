"""
Tests for quiz endpoint error paths and edge cases.
"""
import json
import pytest
from unittest.mock import patch


class TestGenerateQuizErrorPaths:
    """Test error paths in quiz generation."""

    def test_generate_quiz_missing_file_path(self, client, auth_headers, uploaded_document, tmp_path):
        """Test quiz generation when document file path is not found."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            # Mock get_document_path to return None
            with patch("app.crud.documents.get_document_path") as mock_path:
                mock_path.return_value = None
                
                response = client.post(
                    "/quizzes/generate",
                    headers=auth_headers,
                    json={
                        "document_id": doc_id,
                        "num_questions": 5
                    }
                )
                
                # Should return 404 error (line 38)
                assert response.status_code == 404
                assert "File path not found" in response.json()["detail"]

    def test_generate_quiz_llm_failure(self, client, auth_headers, uploaded_document, tmp_path):
        """Test quiz generation when LLM fails."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.quizzes.generate_content") as mock_llm:
                # Make LLM raise an exception
                mock_llm.side_effect = Exception("API rate limit exceeded")
                
                response = client.post(
                    "/quizzes/generate",
                    headers=auth_headers,
                    json={
                        "document_id": doc_id,
                        "num_questions": 5
                    }
                )
                
                # Should return 500 error (lines 54-57)
                assert response.status_code == 500
                assert "Failed to process generated quiz" in response.json()["detail"]
                assert "API rate limit exceeded" in response.json()["detail"]

    def test_generate_quiz_invalid_json_response(self, client, auth_headers, uploaded_document, tmp_path):
        """Test quiz generation when LLM returns invalid JSON."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.quizzes.generate_content") as mock_llm:
                # Return invalid JSON
                mock_llm.return_value = "This is not valid JSON"
                
                response = client.post(
                    "/quizzes/generate",
                    headers=auth_headers,
                    json={
                        "document_id": doc_id,
                        "num_questions": 5
                    }
                )
                
                # Should return 500 error due to JSON parsing failure
                assert response.status_code == 500
                assert "Failed to process generated quiz" in response.json()["detail"]


class TestDeleteQuizPermissions:
    """Test permission checks in quiz deletion."""

    def test_delete_quiz_permission_check(self, client, auth_headers, created_quiz, test_user_data, setup_test_db):
        """Test that permission check runs when non-owner tries to delete a public quiz."""
        quiz_id = created_quiz["quiz_id"]
        
        # Make the quiz public so it can be found by non-owner
        cursor = setup_test_db.cursor()
        cursor.execute(
            "UPDATE quizzes SET access = ? WHERE quiz_id = ?",
            ("public", quiz_id)
        )
        setup_test_db.commit()
        
        # Register a second user
        second_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "full_name": "Other User",
            "password": "otherpass123"
        }
        client.post("/register", json=second_user_data)
        
        # Login as second user
        token_response = client.post(
            "/token",
            data={
                "username": second_user_data["username"],
                "password": second_user_data["password"]
            }
        )
        other_token = token_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to delete public quiz as non-owner
        response = client.delete(
            f"/quizzes/{quiz_id}",
            headers=other_headers
        )
        
        # Should return 403 forbidden (line 72 - permission check)
        assert response.status_code == 403
        assert "don't have permission" in response.json()["detail"]
        
        # Verify quiz still exists
        get_response = client.get(f"/quizzes/{quiz_id}", headers=auth_headers)
        assert get_response.status_code == 200
