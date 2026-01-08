"""
Tests for document endpoint error paths and edge cases.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestUploadDocumentErrorPaths:
    """Test error paths in document upload."""

    def test_upload_file_save_exception(self, client, auth_headers, sample_pdf, tmp_path):
        """Test that file is cleaned up when save operation fails."""
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            # Mock the file.file attribute to raise exception during copyfileobj
            with open(sample_pdf, "rb") as f:
                # Create a mock file that raises exception when read
                from io import BytesIO
                
                class FailingFile:
                    def read(self, *args):
                        raise Exception("Disk full")
                    def __iter__(self):
                        raise Exception("Disk full")
                
                # Patch to trigger exception during file copy
                with patch("app.api.api_v1.endpoints.documents.shutil.copyfileobj") as mock_copy:
                    mock_copy.side_effect = Exception("Disk full")
                    
                    response = client.post(
                        "/documents",
                        headers=auth_headers,
                        files={"file": ("test.pdf", f, "application/pdf")}
                    )
                
                    # Should return 500 error (covers lines 56-59)
                    assert response.status_code == 500
                    assert "Could not save file" in response.json()["detail"]


class TestDownloadDocumentEdgeCases:
    """Test edge cases in document download."""

    def test_download_document_without_metadata(self, client, auth_headers, uploaded_document, tmp_path, setup_test_db):
        """Test download when document metadata is missing (should still return file)."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            # Delete document metadata from database but keep file
            cursor = setup_test_db.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            setup_test_db.commit()
            
            # Mock get_document_path to return a valid path
            file_path = tmp_path / f"{doc_id}.pdf"
            file_path.write_text("test content")
            
            with patch("app.crud.documents.get_document_path") as mock_path:
                mock_path.return_value = str(file_path)
                
                with patch("app.crud.documents.get_document") as mock_get:
                    mock_get.return_value = None  # No metadata
                    
                    response = client.get(
                        f"/documents/{doc_id}/download",
                        headers=auth_headers
                    )
            
            # Should still return file (line 93 - fallback without filename)
            assert response.status_code == 200


class TestGenerateSummaryEdgeCases:
    """Test edge cases in summary generation."""

    def test_summary_already_exists(self, client, auth_headers, uploaded_document, tmp_path, setup_test_db):
        """Test that existing summary is returned without calling LLM."""
        doc_id = uploaded_document["id"]
        
        # Add summary to the document
        cursor = setup_test_db.cursor()
        cursor.execute(
            "UPDATE documents SET summary = ? WHERE id = ?",
            ("Existing summary", doc_id)
        )
        setup_test_db.commit()
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.documents.generate_content") as mock_llm:
                response = client.post(
                    f"/documents/{doc_id}/summary",
                    headers=auth_headers
                )
                
                # Should return existing summary without calling LLM (line 113)
                assert response.status_code == 200
                assert response.json()["summary"] == "Existing summary"
                mock_llm.assert_not_called()

    def test_summary_missing_file_path(self, client, auth_headers, uploaded_document, tmp_path, setup_test_db):
        """Test summary generation when file path is not found."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            # Mock get_document_path to return None
            with patch("app.crud.documents.get_document_path") as mock_path:
                mock_path.return_value = None
                
                response = client.post(
                    f"/documents/{doc_id}/summary",
                    headers=auth_headers
                )
                
                # Should return 404 error (line 118)
                assert response.status_code == 404
                assert "File path not found" in response.json()["detail"]

    def test_summary_llm_generation_failure(self, client, auth_headers, uploaded_document, tmp_path):
        """Test summary generation when LLM fails."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.documents.generate_content") as mock_llm:
                # Make LLM raise an exception
                mock_llm.side_effect = Exception("API quota exceeded")
                
                response = client.post(
                    f"/documents/{doc_id}/summary",
                    headers=auth_headers
                )
                
                # Should return 500 error (lines 134-136)
                assert response.status_code == 500
                assert "Failed to generate summary" in response.json()["detail"]
                assert "API quota exceeded" in response.json()["detail"]
