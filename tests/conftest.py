"""
Pytest configuration and fixtures for ExamMateBE tests.
"""
import os
import sqlite3
import time
import pytest
from unittest.mock import patch, MagicMock

# Set test environment variables BEFORE importing app modules
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


# --------------------------------------------------------------------------
# Database Fixtures
# --------------------------------------------------------------------------

def create_test_tables(conn: sqlite3.Connection):
    """Create all tables in the test database."""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            hashed_password TEXT,
            disabled BOOLEAN,
            language TEXT DEFAULT 'en',
            created_at INTEGER
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id TEXT PRIMARY KEY,
            owned_by TEXT,
            access TEXT,
            quiz_title TEXT,
            created_at INTEGER,
            FOREIGN KEY (owned_by) REFERENCES users (username)
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id TEXT,
            id TEXT,
            question TEXT,
            options TEXT,
            answer_index INTEGER,
            correct_answer TEXT,
            why_correct TEXT,
            created_at INTEGER,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            file_path TEXT,
            owner TEXT,
            summary TEXT,
            created_at INTEGER,
            disabled BOOLEAN DEFAULT 0,
            FOREIGN KEY (owner) REFERENCES users (username)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            start_date INTEGER,
            end_date INTEGER,
            created_at INTEGER,
            updated_at INTEGER,
            owned_by TEXT,
            FOREIGN KEY (owned_by) REFERENCES users (username)
        );
    """)
    
    conn.commit()


# Global test database connection
_test_db_conn = None


def get_test_db_connection():
    """Return the test database connection."""
    global _test_db_conn
    return _test_db_conn


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create an in-memory SQLite database for each test and patch all CRUD modules."""
    global _test_db_conn
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    create_test_tables(conn)
    _test_db_conn = conn
    
    # Patch get_db_connection in all CRUD modules
    with patch("app.crud.user.get_db_connection", get_test_db_connection), \
         patch("app.crud.documents.get_db_connection", get_test_db_connection), \
         patch("app.crud.quizzes.get_db_connection", get_test_db_connection), \
         patch("app.crud.schedule.get_db_connection", get_test_db_connection):
        yield conn
    
    conn.close()
    _test_db_conn = None


@pytest.fixture(scope="function")
def client(setup_test_db):
    """Create a test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client


# --------------------------------------------------------------------------
# Authentication Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def test_user_data():
    """Test user data for registration."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Register a test user and return the user data."""
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    return test_user_data


@pytest.fixture
def auth_token(client, registered_user):
    """Login the registered user and return the auth token."""
    response = client.post(
        "/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with Bearer token for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


# --------------------------------------------------------------------------
# Document Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a minimal valid PDF file for testing."""
    pdf_path = tmp_path / "test_document.pdf"
    with open("tests/test_document_pdf.pdf", "rb") as f:
        pdf_path.write_bytes(f.read())
    return pdf_path

@pytest.fixture
def uploaded_document(client, auth_headers, sample_pdf, tmp_path):
    """Upload a document and return the document data."""
    with patch("app.api.api_v1.endpoints.documents.UPLOAD_DIR", tmp_path):
        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/documents",
                headers=auth_headers,
                files={"file": ("test_document.pdf", f, "application/pdf")}
            )
        assert response.status_code == 200, f"Upload failed: {response.json()}"
        return response.json()


# --------------------------------------------------------------------------
# Quiz Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for quiz generation."""
    return {
        "title": "Test Quiz",
        "questions": [
            {
                "question": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "answer_index": 1,
                "why_correct": "2+2 equals 4"
            }
        ]
    }


@pytest.fixture
def created_quiz(client, auth_headers, uploaded_document, tmp_path, mock_llm_response):
    """Create a quiz using mocked LLM and return the quiz data."""
    import json
    
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
            assert response.status_code == 200, f"Quiz creation failed: {response.json()}"
            return response.json()


# --------------------------------------------------------------------------
# Schedule Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def schedule_data():
    """Sample schedule data for testing."""
    current_time = int(time.time())
    return {
        "title": "Test Schedule",
        "description": "A test schedule item",
        "start_date": current_time,
        "end_date": current_time + 3600  # 1 hour later
    }


@pytest.fixture
def created_schedule(client, auth_headers, schedule_data):
    """Create a schedule and return the schedule data."""
    response = client.post(
        "/schedule",
        headers=auth_headers,
        json=schedule_data
    )
    assert response.status_code == 200, f"Schedule creation failed: {response.json()}"
    return response.json()
