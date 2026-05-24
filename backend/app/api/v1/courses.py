"""
Router: Quản lý môn học (Courses)
Endpoints:
  GET    /api/v1/courses                                  — Danh sách môn học
  POST   /api/v1/courses                                  — ADMIN: tạo môn học
  GET    /api/v1/courses/{course_id}                      — Chi tiết môn học
  PUT    /api/v1/courses/{course_id}                      — ADMIN: cập nhật
  DELETE /api/v1/courses/{course_id}                      — ADMIN: xóa
  POST   /api/v1/courses/{course_id}/prerequisites        — ADMIN: thêm môn tiên quyết
  DELETE /api/v1/courses/{course_id}/prerequisites/{prereq_id} — ADMIN: gỡ
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Course, CoursePrerequisite, User
from app.schemas.curriculum import (
    CourseCreate, CourseUpdate, CourseResponse,
    CoursePrerequisiteCreate, CoursePrerequisiteResponse
)

router = APIRouter(prefix="/courses", tags=["Môn học"])


@router.get("", response_model=list[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Lấy danh sách tất cả môn học."""
    courses = db.query(Course).all()
    return courses


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Tạo môn học mới. Chỉ ADMIN."""
    if db.query(Course).filter(Course.course_id == data.course_id).first():
        raise HTTPException(status_code=400, detail=f"CourseID '{data.course_id}' đã tồn tại")

    course = Course(course_id=data.course_id, course_name=data.course_name)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem chi tiết môn học kèm danh sách môn tiên quyết."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: str,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Cập nhật môn học. Chỉ ADMIN."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")

    if data.course_name:
        course.course_name = data.course_name

    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Xóa môn học. Chỉ ADMIN."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    db.delete(course)
    db.commit()


@router.post("/{course_id}/prerequisites", response_model=CoursePrerequisiteResponse, status_code=201)
def add_prerequisite(
    course_id: str,
    data: CoursePrerequisiteCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Thêm môn tiên quyết cho môn học. Chỉ ADMIN."""
    if not db.query(Course).filter(Course.course_id == course_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    if not db.query(Course).filter(Course.course_id == data.prerequisite_course_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy môn tiên quyết")
    if course_id == data.prerequisite_course_id:
        raise HTTPException(status_code=400, detail="Môn học không thể là tiên quyết của chính nó")

    existing = db.query(CoursePrerequisite).filter(
        CoursePrerequisite.course_id == course_id,
        CoursePrerequisite.prerequisite_course_id == data.prerequisite_course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Môn tiên quyết này đã được thêm rồi")

    prereq = CoursePrerequisite(
        course_id=course_id,
        prerequisite_course_id=data.prerequisite_course_id
    )
    db.add(prereq)
    db.commit()
    db.refresh(prereq)
    return prereq


@router.delete("/{course_id}/prerequisites/{prereq_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_prerequisite(
    course_id: str,
    prereq_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Gỡ môn tiên quyết. Chỉ ADMIN."""
    prereq = db.query(CoursePrerequisite).filter(
        CoursePrerequisite.course_id == course_id,
        CoursePrerequisite.prerequisite_course_id == prereq_id
    ).first()
    if not prereq:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn tiên quyết này")
    db.delete(prereq)
    db.commit()
