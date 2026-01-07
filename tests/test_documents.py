"""
Tests for document endpoints: upload, list, get, search, download, summary, delete.
"""
import pytest
from unittest.mock import patch


class TestUploadDocumentEndpoint:
    """Tests for POST /documents endpoint."""

    def test_upload_pdf_success(self, client, auth_headers, sample_pdf, tmp_path):
        """Test successful PDF upload."""
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with open(sample_pdf, "rb") as f:
                response = client.post(
                    "/documents",
                    headers=auth_headers,
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert "id" in data

    def test_upload_invalid_file_type(self, client, auth_headers, tmp_path):
        """Test upload fails for supported files."""
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            response = client.post(
                "/documents",
                headers=auth_headers,
                files={"file": ("test.docx", b"hello world", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_unauthorized(self, client, sample_pdf):
        """Test upload requires authentication."""
        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/documents",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 401


class TestGetDocumentsEndpoint:
    """Tests for GET /documents endpoint."""

    def test_get_documents_empty(self, client, auth_headers):
        """Test getting documents when none exist."""
        response = client.get("/documents", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_documents_with_uploads(self, client, auth_headers, uploaded_document):
        """Test getting documents after upload."""
        response = client.get("/documents", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == uploaded_document["id"]


class TestSearchDocumentsEndpoint:
    """Tests for GET /documents/search endpoint."""

    def test_search_documents_found(self, client, auth_headers, uploaded_document):
        """Test searching for uploaded document."""
        response = client.get(
            "/documents/search",
            headers=auth_headers,
            params={"q": "test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_search_documents_not_found(self, client, auth_headers, uploaded_document):
        """Test searching for non-existent document."""
        response = client.get(
            "/documents/search",
            headers=auth_headers,
            params={"q": "nonexistent_xyz"}
        )
        
        assert response.status_code == 200
        assert response.json() == []


class TestGetDocumentEndpoint:
    """Tests for GET /documents/{doc_id} endpoint."""

    def test_get_document_success(self, client, auth_headers, uploaded_document):
        """Test getting a specific document."""
        doc_id = uploaded_document["id"]
        response = client.get(f"/documents/{doc_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["id"] == doc_id

    def test_get_document_not_found(self, client, auth_headers):
        """Test getting non-existent document."""
        response = client.get("/documents/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404


class TestDownloadDocumentEndpoint:
    """Tests for GET /documents/{doc_id}/download endpoint."""

    def test_download_document_success(self, client, auth_headers, uploaded_document, tmp_path):
        """Test downloading a document."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            response = client.get(
                f"/documents/{doc_id}/download",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")

    def test_download_document_not_found(self, client, auth_headers):
        """Test downloading non-existent document."""
        response = client.get(
            "/documents/nonexistent-id/download",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestGenerateSummaryEndpoint:
    """Tests for POST /documents/{doc_id}/summary endpoint."""

    def test_generate_summary_success(self, client, auth_headers, uploaded_document, tmp_path):
        """Test generating summary with mocked LLM."""
        doc_id = uploaded_document["id"]
        
        with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
            with patch("app.api.api_v1.endpoints.documents.generate_content") as mock_llm:
                mock_llm.return_value = "This is a test summary of the document."
                
                response = client.post(
                    f"/documents/{doc_id}/summary",
                    headers=auth_headers
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "This is a test summary of the document."

    def test_generate_summary_not_found(self, client, auth_headers):
        """Test generating summary for non-existent document."""
        response = client.post(
            "/documents/nonexistent-id/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestDeleteDocumentEndpoint:
    """Tests for DELETE /documents/{doc_id} endpoint."""

    def test_delete_document_success(self, client, auth_headers, uploaded_document):
        """Test soft deleting a document."""
        doc_id = uploaded_document["id"]
        response = client.delete(f"/documents/{doc_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify document is no longer accessible
        get_response = client.get(f"/documents/{doc_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_document_not_found(self, client, auth_headers):
        """Test deleting non-existent document."""
        response = client.delete("/documents/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404
