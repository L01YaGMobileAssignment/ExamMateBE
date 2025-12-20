import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from app.api.deps import CurrentUser
from app.core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.schemas.documents import DocumentCreate
import app.crud.documents as documents_crud

router = APIRouter()

@router.post("/documents", response_model=DocumentCreate)
async def upload_document(
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF or DOCX) to the server.
    """
    # Create upload dir if it doesn't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and DOCX are allowed."
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