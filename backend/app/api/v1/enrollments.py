"""
Router: Quản lý đăng ký học tập (Enrollments)
Đây là module trung tâm: sinh viên đăng ký lớp, giáo viên nhập điểm.

Endpoints:
  GET    /api/v1/enrollments                        — Danh sách (filter đa dạng)
  POST   /api/v1/enrollments                        — Đăng ký lớp (STUDENT/ADMIN)
  GET    /api/v1/enrollments/{class_id}/{student_id} — Chi tiết enrollment
  PUT    /api/v1/enrollments/{class_id}/{student_id} — Nhập điểm (TEACHER/ADMIN)
  DELETE /api/v1/enrollments/{class_id}/{student_id} — Hủy đăng ký (ADMIN)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Enrollment, Class, Student, User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse

router = APIRouter(prefix="/enrollments", tags=["Đăng ký học tập"])


@router.get("", response_model=list[EnrollmentResponse])
def list_enrollments(
    student_id: str | None = Query(None, description="Lọc theo sinh viên"),
    class_id: str | None   = Query(None, description="Lọc theo lớp học"),
    course_id: str | None  = Query(None, description="Lọc theo môn học"),
    status_: str | None    = Query(None, alias="status", description="STUDYING | PASSED | FAILED"),
    page: int              = Query(1, ge=1),
    page_size: int         = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách enrollment với nhiều bộ lọc.
    - STUDENT: tự động lọc theo user_id của mình
    - TEACHER/ADMIN: lọc theo tham số tùy ý
    """
    query = db.query(Enrollment)

    # Sinh viên chỉ xem được đăng ký của chính mình
    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids:
        query = query.filter(Enrollment.student_id == current_user.user_id)
    else:
        if student_id:
            query = query.filter(Enrollment.student_id == student_id)

    if class_id:
        query = query.filter(Enrollment.class_id == class_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    if status_:
        query = query.filter(Enrollment.status == status_)

    enrollments = query.offset((page - 1) * page_size).limit(page_size).all()
    return enrollments



@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đăng ký lớp học.
    - STUDENT: chỉ đăng ký cho bản thân
    - ADMIN: đăng ký cho bất kỳ sinh viên nào
    """
    role_ids = [ur.role_id for ur in current_user.user_roles]
    # Sinh viên chỉ được đăng ký cho chính mình
    if "STUDENT" in role_ids and "ADMIN" not in role_ids:
        if data.student_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được đăng ký cho bản thân")

    # Kiểm tra lớp học tồn tại
    class_ = db.query(Class).filter(
        Class.course_id == data.course_id,
        Class.class_id == data.class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    # Kiểm tra sinh viên tồn tại
    if not db.query(Student).filter(Student.user_id == data.student_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    # Kiểm tra chưa đăng ký lớp này
    existing = db.query(Enrollment).filter(
        Enrollment.class_id == data.class_id,
        Enrollment.student_id == data.student_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký lớp này rồi")

    # Kiểm tra còn chỗ không
    if class_.capacity:
        current_count = db.query(Enrollment).filter(
            Enrollment.class_id == data.class_id,
            Enrollment.course_id == data.course_id
        ).count()
        if current_count >= class_.capacity:
            raise HTTPException(status_code=400, detail="Lớp học đã đầy")

    # Tạo enrollment với trạng thái "STUDYING"
    enrollment = Enrollment(
        class_id=data.class_id,
        course_id=data.course_id,
        student_id=data.student_id,
        status="STUDYING"
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/{class_id}/{student_id}", response_model=EnrollmentResponse)
def get_enrollment(
    class_id: str,
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xem chi tiết một enrollment (điểm số, trạng thái)."""
    role_ids = [ur.role_id for ur in current_user.user_roles]
    # Sinh viên chỉ xem của mình
    if "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids:
        if current_user.user_id != student_id:
            raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")

    enrollment = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")
    return enrollment


@router.put("/{class_id}/{student_id}", response_model=EnrollmentResponse)
def update_enrollment(
    class_id: str,
    student_id: str,
    data: EnrollmentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN", "TEACHER"))  # Chỉ TEACHER/ADMIN nhập điểm
):
    """
    Cập nhật điểm số và trạng thái enrollment.
    Thường dùng để: nhập điểm giữa kỳ, cuối kỳ, xếp loại.
    Chỉ TEACHER và ADMIN.
    """
    enrollment = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(enrollment, field, value)

    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.delete("/{class_id}/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_enrollment(
    class_id: str,
    student_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))  # Chỉ ADMIN hủy đăng ký
):
    """Hủy đăng ký học. Chỉ ADMIN."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")
    db.delete(enrollment)
    db.commit()
