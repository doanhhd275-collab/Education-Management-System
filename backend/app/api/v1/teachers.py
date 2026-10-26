"""
Router: Quản lý giáo viên (Teachers)
Endpoints:
  GET  /api/v1/teachers                      — ADMIN: danh sách giáo viên
  POST /api/v1/teachers                      — ADMIN: tạo bản ghi teacher
  GET  /api/v1/teachers/me                   — giáo viên xem thông tin của mình
  GET  /api/v1/teachers/{teacher_id}         — xem profile giáo viên
  GET  /api/v1/teachers/{teacher_id}/classes — xem lớp đang dạy
"""
from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.user import TeacherCreate, TeacherResponse
from app.services.teacher_service import TeacherService

router = APIRouter(prefix="/teachers", tags=["Quản lý giáo viên"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Lấy danh sách giáo viên. Chỉ ADMIN."""
    return TeacherService.list_teachers(db, page, page_size)


@router.post("", response_model=TeacherResponse, status_code=201)
def create_teacher(data: TeacherCreate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Tạo bản ghi Teacher và gán vào User đã có. Chỉ ADMIN."""
    return TeacherService.create_teacher(db, data.teacher_id, data.user_id)


@router.get("/me")
def get_my_teacher_info(db: DbDep = None, current_user: CurrentUserDep = None):
    """Lấy thông tin teacher của user đang đăng nhập."""
    return TeacherService.get_my_info(db, current_user.user_id)


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem profile giáo viên. Mọi user đã đăng nhập đều xem được."""
    return TeacherService.get_teacher(db, teacher_id)


@router.get("/{teacher_id}/classes")
def get_teacher_classes(
    teacher_id: str,
    semester: str | None = Query(None, description="Lọc theo học kỳ"),
    db: DbDep = None,
    _: CurrentUserDep = None,
):
    """Lấy danh sách lớp mà giáo viên đang/đã dạy."""
    return TeacherService.get_classes(db, teacher_id, semester)
