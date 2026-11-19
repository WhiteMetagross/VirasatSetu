import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.models import Document, User
from app.schemas.schemas import DocumentResponse
from app.utils.auth import get_current_user
from app.utils.security import validate_file_upload

router = APIRouter(prefix="/api/documents", tags=["Document Storage"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    deceased_person_id: str = Form(None),
    claimant_id: str = Form(None),
    claim_id: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    # Validate extension, file size, and MIME type against arbitrary upload attacks
    safe_filename = validate_file_upload(file.filename or "document.pdf", content, file.content_type)

    ext = os.path.splitext(safe_filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    file_size = len(content)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    doc = Document(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        deceased_person_id=deceased_person_id if deceased_person_id else None,
        claimant_id=claimant_id if claimant_id else None,
        claim_id=claim_id if claim_id else None,
        document_type=document_type,
        file_name=safe_filename,
        file_path=file_path,
        file_size=file_size,
        content_type=file.content_type
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Access control: prevent Insecure Direct Object Reference (IDOR) attacks
    is_owner = (doc.user_id == current_user.id)
    is_admin = (current_user.role == "admin")
    is_institution = (current_user.role == "institution_rep")
    if not (is_owner or is_admin or is_institution):
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")

    return FileResponse(
        path=doc.file_path,
        filename=doc.file_name,
        media_type=doc.content_type or "application/octet-stream"
    )
