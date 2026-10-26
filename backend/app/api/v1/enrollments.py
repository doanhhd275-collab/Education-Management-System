"""
Router: Quản lý đăng ký học tập (Enrollments)
Endpoints:
  GET    /api/v1/enrollments                         — Danh sách (filter đa dạng)
  POST   /api/v1/enrollments                         — Đăng ký lớp (STUDENT/ADMIN)
  GET    /api/v1/enrollments/{class_id}/{student_id} — Chi tiết enrollment
  PUT    /api/v1/enrollments/{class_id}/{student_id} — Nhập điểm (TEACHER/ADMIN)
  DELETE /api/v1/enrollments/{class_id}/{student_id} — Hủy đăng ký (ADMIN)
"""
from fastapi import APIRouter, Depends, status, Query

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Đăng ký học tập"])


@router.get("", response_model=list[EnrollmentResponse])
def list_enrollments(
    student_id: str | None = Query(None),
    class_id: str | None   = Query(None),
    course_id: str | None  = Query(None),
    status_: str | None    = Query(None, alias="status"),
    page: int              = Query(1, ge=1),
    page_size: int         = Query(20, ge=1, le=100),
    db: DbDep = None,
    current_user: CurrentUserDep = None,
):
    """Lấy danh sách enrollment — STUDENT chỉ thấy của mình."""
    return EnrollmentService.list_enrollments(db, current_user, student_id, class_id, course_id, status_, page, page_size)


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll(data: EnrollmentCreate, db: DbDep = None, current_user: CurrentUserDep = None):
    """Đăng ký lớp học — STUDENT chỉ đăng ký cho bản thân, ADMIN cho bất kỳ ai."""
    return EnrollmentService.enroll(db, current_user, data.class_id, data.course_id, data.student_id)


@router.get("/{class_id}/{student_id}", response_model=EnrollmentResponse)
def get_enrollment(class_id: str, student_id: str, db: DbDep = None, current_user: CurrentUserDep = None):
    """Xem chi tiết một enrollment."""
    return EnrollmentService.get_enrollment(db, current_user, class_id, student_id)


@router.put("/{class_id}/{student_id}", response_model=EnrollmentResponse)
def update_enrollment(
    class_id: str,
    student_id: str,
    data: EnrollmentUpdate,
    db: DbDep = None,
    _=Depends(require_role("TEACHER")),
):
    """Cập nhật điểm số và trạng thái enrollment. Chỉ TEACHER."""
    return EnrollmentService.update_enrollment(db, class_id, student_id, data.model_dump(exclude_none=True))


@router.delete("/{class_id}/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_enrollment(class_id: str, student_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Hủy đăng ký học. Chỉ ADMIN."""
    EnrollmentService.cancel_enrollment(db, class_id, student_id)
