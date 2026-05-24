"""
Router: Quản lý sinh viên (Students)
Quyền truy cập:
  - ADMIN: toàn quyền
  - TEACHER: xem danh sách sinh viên trong lớp của mình
  - STUDENT: chỉ xem thông tin và tiến độ của bản thân

Endpoints:
  GET /api/v1/students                        — ADMIN/TEACHER: danh sách sinh viên
  GET /api/v1/students/{user_id}              — xem profile sinh viên
  PUT /api/v1/students/{user_id}              — ADMIN: cập nhật GPA, CPA, warning
  GET /api/v1/students/{user_id}/enrollments  — xem danh sách lớp đã đăng ký
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import User, Student, Enrollment
from app.schemas.user import StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Quản lý sinh viên"])


@router.get("", response_model=list[StudentResponse])
def list_students(
    program_id: str | None = Query(None, description="Lọc theo chương trình đào tạo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN", "TEACHER"))
):
    """Lấy danh sách sinh viên. ADMIN và TEACHER được xem."""
    query = db.query(Student).options(joinedload(Student.user))

    if program_id:
        query = query.filter(Student.program_id == program_id)

    students = query.offset((page - 1) * page_size).limit(page_size).all()
    return students


@router.get("/{user_id}", response_model=StudentResponse)
def get_student(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xem profile sinh viên.
    - ADMIN/TEACHER: xem được tất cả
    - STUDENT: chỉ xem của bản thân
    """
    # Dùng role_id (ADMIN/TEACHER) thay vì role_name (tiếng Việt)
    role_ids = [ur.role_id for ur in current_user.user_roles]
    is_admin_or_teacher = "ADMIN" in role_ids or "TEACHER" in role_ids
    if not is_admin_or_teacher and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")

    student = (
        db.query(Student)
        .options(joinedload(Student.user))
        .filter(Student.user_id == user_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return student


@router.put("/{user_id}", response_model=StudentResponse)
def update_student(
    user_id: str,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Cập nhật điểm GPA, CPA, mức cảnh báo. Chỉ ADMIN."""
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.get("/{user_id}/enrollments")
def get_student_enrollments(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xem danh sách lớp học mà sinh viên đã đăng ký + điểm số.
    STUDENT chỉ xem được của bản thân.
    """
    role_ids = [ur.role_id for ur in current_user.user_roles]
    is_admin_or_teacher = "ADMIN" in role_ids or "TEACHER" in role_ids
    if not is_admin_or_teacher and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")

    enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == user_id)
        .all()
    )

    # Trả về dữ liệu đơn giản, dễ đọc
    result = []
    for e in enrollments:
        result.append({
            "class_id":         e.class_id,
            "course_id":        e.course_id,
            "midterm_score":    e.midterm_score,
            "final_term_score": e.final_term_score,
            "grade":            e.grade,
            "status":           e.status,
        })
    return result
