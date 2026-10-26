"""
Router: Quản lý sinh viên (Students)
Endpoints:
  GET /api/v1/students                        — ADMIN/TEACHER: danh sách sinh viên
  GET /api/v1/students/{user_id}              — xem profile sinh viên
  PUT /api/v1/students/{user_id}              — ADMIN: cập nhật GPA, CPA, warning
  GET /api/v1/students/{user_id}/enrollments  — xem danh sách lớp đã đăng ký
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_db, get_current_user, require_role, DbDep, CurrentUserDep
from app.schemas.user import StudentResponse, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Quản lý sinh viên"])


@router.get("", response_model=list[StudentResponse])
def list_students(
    program_id: str | None = Query(None, description="Lọc theo chương trình đào tạo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbDep = None,
    _=Depends(require_role("ADMIN", "TEACHER")),
):
    """Lấy danh sách sinh viên. ADMIN và TEACHER được xem."""
    return StudentService.list_students(db, program_id, page, page_size)


@router.get("/{user_id}", response_model=StudentResponse)
def get_student(user_id: str, db: DbDep = None, current_user: CurrentUserDep = None):
    """
    Xem profile sinh viên.
    - ADMIN/TEACHER: xem được tất cả
    - STUDENT: chỉ xem của bản thân
    """
    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in role_ids and "TEACHER" not in role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")
    return StudentService.get_student(db, user_id)


@router.put("/{user_id}", response_model=StudentResponse)
def update_student(
    user_id: str,
    data: StudentUpdate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Cập nhật điểm GPA, CPA, mức cảnh báo. Chỉ ADMIN."""
    return StudentService.update_student(db, user_id, data.model_dump(exclude_none=True))


@router.get("/{user_id}/enrollments")
def get_student_enrollments(user_id: str, db: DbDep = None, current_user: CurrentUserDep = None):
    """Xem danh sách lớp học + điểm số. STUDENT chỉ xem được của bản thân."""
    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in role_ids and "TEACHER" not in role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")
    return StudentService.get_enrollments(db, user_id)
