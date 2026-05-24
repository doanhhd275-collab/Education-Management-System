"""
Router: Quản lý tài liệu học tập (Documents)
Endpoints:
  GET    /api/v1/documents                    — Danh sách tài liệu
  POST   /api/v1/documents                    — TEACHER: đăng tài liệu mới
  GET    /api/v1/documents/{document_id}      — Xem chi tiết
  PUT    /api/v1/documents/{document_id}      — TEACHER (của mình) hoặc ADMIN: cập nhật
  DELETE /api/v1/documents/{document_id}      — TEACHER (của mình) hoặc ADMIN: xóa
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Document, Teacher, User
from app.schemas.assignment import DocumentCreate, DocumentUpdate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["Tài liệu học tập"])


def _get_teacher_by_user(db: Session, user_id: str) -> Teacher | None:
    """Helper: lấy Teacher record từ user_id."""
    return db.query(Teacher).filter(Teacher.user_id == user_id).first()


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    teacher_id: str | None = Query(None, description="Lọc theo giáo viên"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Mọi user đăng nhập đều xem được
):
    """Lấy danh sách tài liệu học tập."""
    query = db.query(Document)

    if teacher_id:
        query = query.filter(Document.teacher_id == teacher_id)

    documents = query.offset((page - 1) * page_size).limit(page_size).all()
    return documents


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đăng tài liệu mới. TEACHER hoặc ADMIN.
    Giáo viên chỉ được đăng với teacher_id của chính mình.
    """
    role_ids = [ur.role_id for ur in current_user.user_roles]

    # Kiểm tra quyền
    if "TEACHER" not in role_names and "ADMIN" not in role_names:
        raise HTTPException(status_code=403, detail="Chỉ giáo viên hoặc admin mới được đăng tài liệu")

    # Giáo viên chỉ đăng dưới tên mình
    if "TEACHER" in role_ids and "ADMIN" not in role_names:
        teacher = _get_teacher_by_user(db, current_user.user_id)
        if not teacher or teacher.teacher_id != data.teacher_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được đăng tài liệu với TeacherID của bản thân")

    # Kiểm tra teacher_id tồn tại
    if not db.query(Teacher).filter(Teacher.teacher_id == data.teacher_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Kiểm tra document_id chưa tồn tại
    if db.query(Document).filter(Document.document_id == data.document_id).first():
        raise HTTPException(status_code=400, detail=f"DocumentID '{data.document_id}' đã tồn tại")

    doc = Document(
        document_id=data.document_id,
        document_name=data.document_name,
        deadline=data.deadline,
        teacher_id=data.teacher_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem chi tiết tài liệu."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return doc


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật tài liệu. TEACHER của tài liệu đó hoặc ADMIN."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    role_ids = [ur.role_id for ur in current_user.user_roles]

    # Giáo viên chỉ sửa tài liệu của mình
    if "TEACHER" in role_ids and "ADMIN" not in role_names:
        teacher = _get_teacher_by_user(db, current_user.user_id)
        if not teacher or doc.teacher_id != teacher.teacher_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được sửa tài liệu của mình")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(doc, field, value)

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa tài liệu. TEACHER của tài liệu đó hoặc ADMIN."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "TEACHER" in role_ids and "ADMIN" not in role_names:
        teacher = _get_teacher_by_user(db, current_user.user_id)
        if not teacher or doc.teacher_id != teacher.teacher_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được xóa tài liệu của mình")

    db.delete(doc)
    db.commit()
