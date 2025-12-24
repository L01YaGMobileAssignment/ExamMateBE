import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from app.api.deps import CurrentUser
from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.schemas.documents import DocumentCreate
import app.crud.documents as documents_crud
from google.genai import types
from app.core.config import SUMMARY_SYSTEM_PROMPT
from app.services.llm import generate_content

router = APIRouter()

@router.post("/documents", response_model=DocumentCreate)
async def upload_document(
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF) to the server.
    """
    # Create upload dir if it doesn't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF are allowed."
        )
    
    # Generate unique ID
    doc_id = str(uuid.uuid4())
    unique_filename = f"{doc_id}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Save to DB via CRUD
        doc = documents_crud.create_document(
            doc_id=doc_id, 
            filename=file.filename, 
            file_path=str(file_path), 
            owner=current_user.username
        )
        return doc
            
    except Exception as e:
         if file_path.exists():
            file_path.unlink()
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}"
        )

@router.get("/documents", response_model=list[DocumentCreate])
async def get_documents(current_user: CurrentUser):
    return documents_crud.get_documents(current_user.username)

@router.get("/documents/search", response_model=list[DocumentCreate])
async def search_documents(current_user: CurrentUser, q: str):
    return documents_crud.search_documents(current_user.username, q)

@router.get("/documents/{doc_id}", response_model=DocumentCreate)
async def get_document(current_user: CurrentUser, doc_id: str):
    document = documents_crud.get_document(doc_id, current_user.username)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/documents/{doc_id}/download")
async def download_document(current_user: CurrentUser, doc_id: str):
    doc_path = documents_crud.get_document_path(doc_id, current_user.username)
    if not doc_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    document = documents_crud.get_document(doc_id, current_user.username)
    if document:
        return FileResponse(doc_path, filename=document.filename)
    return FileResponse(doc_path)


@router.post("/documents/{doc_id}/summary")
async def generate_summary(current_user: CurrentUser, doc_id: str):
    """
    Generate a summary for a document using Gemini.
    If summary exists in DB, return it.
    Otherwise, call Gemini API, save to DB, and return it.
    """
    # Check if document exists
    document = documents_crud.get_document(doc_id, current_user.username)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
            
    # Return existing summary if available
    if document.summary:
        return document
    
    # Get file path
    doc_path = documents_crud.get_document_path(doc_id, current_user.username)
    if not doc_path:
         raise HTTPException(status_code=404, detail="File path not found")
         
    try:
        generated_text = generate_content(
            file_path=doc_path,
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            generation_config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        documents_crud.update_document_summary(doc_id, current_user.username, generated_text)
        document.summary = generated_text
        return document
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )
