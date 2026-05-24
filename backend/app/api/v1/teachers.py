"""
Router: Quản lý giáo viên (Teachers)
Endpoints:
  GET  /api/v1/teachers                   — ADMIN: danh sách giáo viên
  POST /api/v1/teachers                   — ADMIN: tạo bản ghi teacher
  GET  /api/v1/teachers/{teacher_id}      — xem profile giáo viên
  GET  /api/v1/teachers/{teacher_id}/classes — xem lớp đang dạy
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import User, Teacher, TeacherClass
from app.schemas.user import TeacherCreate, TeacherResponse

router = APIRouter(prefix="/teachers", tags=["Quản lý giáo viên"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Lấy danh sách giáo viên. Chỉ ADMIN."""
    teachers = (
        db.query(Teacher)
        .options(joinedload(Teacher.user))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return teachers


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    data: TeacherCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """
    Tạo bản ghi Teacher và gán vào User đã có.
    User phải tồn tại trước. Chỉ ADMIN.
    """
    # Kiểm tra user tồn tại
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy user '{data.user_id}'")

    # Kiểm tra TeacherID chưa tồn tại
    if db.query(Teacher).filter(Teacher.teacher_id == data.teacher_id).first():
        raise HTTPException(status_code=400, detail=f"TeacherID '{data.teacher_id}' đã tồn tại")

    # Kiểm tra user chưa là teacher
    if db.query(Teacher).filter(Teacher.user_id == data.user_id).first():
        raise HTTPException(status_code=400, detail="User này đã là giáo viên")

    new_teacher = Teacher(teacher_id=data.teacher_id, user_id=data.user_id)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@router.get("/me")
def get_my_teacher_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy thông tin teacher của user đang đăng nhập. Dùng cho trang nhập điểm."""
    teacher = (
        db.query(Teacher)
        .options(joinedload(Teacher.user))
        .filter(Teacher.user_id == current_user.user_id)
        .first()
    )
    if not teacher:
        raise HTTPException(status_code=404, detail="Bạn chưa được đăng ký là giáo viên trong hệ thống")
    return {
        "teacher_id": teacher.teacher_id,
        "user_id":    teacher.user_id,
        "name":       teacher.user.name if teacher.user else "",
    }


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem profile giáo viên. Mọi user đã đăng nhập đều xem được."""
    teacher = (
        db.query(Teacher)
        .options(joinedload(Teacher.user))
        .filter(Teacher.teacher_id == teacher_id)
        .first()
    )
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
    return teacher



@router.get("/{teacher_id}/classes")
def get_teacher_classes(
    teacher_id: str,
    semester: str | None = Query(None, description="Lọc theo học kỳ"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Lấy danh sách lớp mà giáo viên đang/đã dạy."""
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    query = db.query(TeacherClass).filter(TeacherClass.teacher_id == teacher_id)
    if semester:
        query = query.filter(TeacherClass.semester == semester)

    teacher_classes = query.all()
    return [
        {
            "class_id":  tc.class_id,
            "course_id": tc.course_id,
            "semester":  tc.semester,
        }
        for tc in teacher_classes
    ]
