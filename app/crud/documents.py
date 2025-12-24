from app.schemas.documents import DocumentCreate
from app.db.database import get_db_connection
import time

def create_document(doc_id: str, filename: str, file_path: str, owner: str) -> DocumentCreate:
    current_time = int(time.time())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, filename, file_path, owner, created_at, disabled)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, filename, file_path, owner, current_time, False))
        conn.commit()
    return DocumentCreate(id=doc_id, filename=filename, owner=owner, created_at=current_time)

def get_documents(owner: str) -> list[DocumentCreate]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM documents WHERE owner = ? AND disabled = ?
        """, (owner, False))
        documents = cursor.fetchall()
        return [DocumentCreate(**doc) for doc in documents]

def get_document(doc_id: str, owner: str) -> DocumentCreate | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM documents WHERE id = ? AND owner = ? AND disabled = ?
        """, (doc_id, owner, False))
        document = cursor.fetchone()
        if document:
            return DocumentCreate(**document)
        return None

def get_document_path(doc_id: str, owner: str) -> str | None:
     with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM documents WHERE id = ? AND owner = ? AND disabled = ?
        """, (doc_id, owner, False))
        row = cursor.fetchone()
        if row:
            return row["file_path"]
        return None

def update_document_summary(doc_id: str, owner: str, summary: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE documents
            SET summary = ?
            WHERE id = ? AND owner = ?
        """, (summary, doc_id, owner))
        conn.commit()

def search_documents(owner: str, query: str) -> list[DocumentCreate]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        search_query = f"%{query}%"
        cursor.execute("""
            SELECT * FROM documents 
            WHERE owner = ? AND (filename LIKE ? OR summary LIKE ?) AND disabled = ?
        """, (owner, search_query, search_query, False))
        documents = cursor.fetchall()
        return [DocumentCreate(**doc) for doc in documents]
    
def disable_document(doc_id: str, owner: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE documents
            SET disabled = ?
            WHERE id = ? AND owner = ?
        """, (True, doc_id, owner))
        conn.commit()
