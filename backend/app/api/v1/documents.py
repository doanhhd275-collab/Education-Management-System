"""
Router: Quản lý tài liệu học tập (Documents)
Endpoints:
  GET    /api/v1/documents                    — Danh sách tài liệu
  POST   /api/v1/documents                    — TEACHER: đăng tài liệu mới
  GET    /api/v1/documents/{document_id}      — Xem chi tiết
  PUT    /api/v1/documents/{document_id}      — TEACHER (của mình) hoặc ADMIN
  DELETE /api/v1/documents/{document_id}      — TEACHER (của mình) hoặc ADMIN
"""
from fastapi import APIRouter, Query

from app.core.dependencies import DbDep, CurrentUserDep
from app.schemas.assignment import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Tài liệu học tập"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    teacher_id: str | None = Query(None),
    course_id:  str | None = Query(None),
    class_id:   str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbDep = None,
    _: CurrentUserDep = None,
):
    """Lấy danh sách tài liệu học tập."""
    return DocumentService.list_documents(db, teacher_id, course_id, class_id, page, page_size)


@router.post("", response_model=DocumentResponse, status_code=201)
def create_document(data: DocumentCreate, db: DbDep = None, current_user: CurrentUserDep = None):
    """Đăng tài liệu mới. TEACHER hoặc ADMIN."""
    return DocumentService.create_document(
        db, current_user,
        data.document_id, data.document_name, data.deadline,
        data.teacher_id, data.link_url, data.course_id, data.class_id,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem chi tiết tài liệu."""
    return DocumentService.get_document(db, document_id)


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    data: DocumentUpdate,
    db: DbDep = None,
    current_user: CurrentUserDep = None,
):
    """Cập nhật tài liệu. TEACHER của tài liệu đó hoặc ADMIN."""
    return DocumentService.update_document(db, current_user, document_id, data.model_dump(exclude_none=True))


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, db: DbDep = None, current_user: CurrentUserDep = None):
    """Xóa tài liệu. TEACHER của tài liệu đó hoặc ADMIN."""
    DocumentService.delete_document(db, current_user, document_id)
