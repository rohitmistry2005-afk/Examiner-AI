from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.security import get_current_user_id
from app.rag.document_rag import DocumentRAGService
from app.schemas.domain import DocumentRecord

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_rag() -> DocumentRAGService:
    return DocumentRAGService()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    subject: str | None = Form(default=None),
    source_type: str = Form(default="study_material"),
    user_id: UUID = Depends(get_current_user_id),
    service: DocumentRAGService = Depends(get_document_rag),
):
    allowed_source_types = {"syllabus", "study_material", "reference", "other"}
    if source_type not in allowed_source_types:
        raise HTTPException(status_code=422, detail="Invalid document source type.")

    data = await file.read()
    try:
        result = service.ingest(
            user_id=user_id,
            filename=file.filename or "document",
            mime_type=file.content_type or "application/octet-stream",
            data=data,
            subject=subject,
            source_type=source_type,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to process the document.") from exc
