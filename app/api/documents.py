from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import Document, User
from app.services.rag import rag_service


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    content = await file.read()
    chunk_count = rag_service.add_document(file.filename, content)
    document = Document(filename=file.filename, chunk_count=chunk_count)
    db.add(document)
    db.commit()
    return {"filename": file.filename, "chunks_indexed": chunk_count}


@router.get("")
def list_documents(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.created_at.desc()).all()
