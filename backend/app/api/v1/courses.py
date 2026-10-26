"""
Router: Quản lý môn học (Courses)
Endpoints:
  GET    /api/v1/courses                                       — Danh sách môn học
  POST   /api/v1/courses                                       — ADMIN: tạo môn học
  GET    /api/v1/courses/{course_id}                           — Chi tiết môn học
  PUT    /api/v1/courses/{course_id}                           — ADMIN: cập nhật
  DELETE /api/v1/courses/{course_id}                           — ADMIN: xóa
  POST   /api/v1/courses/{course_id}/prerequisites             — ADMIN: thêm môn tiên quyết
  DELETE /api/v1/courses/{course_id}/prerequisites/{prereq_id} — ADMIN: gỡ
"""
from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.curriculum import (
    CourseCreate, CourseUpdate, CourseResponse,
    CoursePrerequisiteCreate, CoursePrerequisiteResponse,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Môn học"])


@router.get("", response_model=list[CourseResponse])
def list_courses(db: DbDep = None, _: CurrentUserDep = None):
    """Lấy danh sách tất cả môn học."""
    return CourseService.list_courses(db)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Tạo môn học mới. Chỉ ADMIN."""
    return CourseService.create_course(db, data.course_id, data.course_name)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem chi tiết môn học kèm danh sách môn tiên quyết."""
    return CourseService.get_course(db, course_id)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: str, data: CourseUpdate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Cập nhật môn học. Chỉ ADMIN."""
    return CourseService.update_course(db, course_id, data.course_name)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Xóa môn học. Chỉ ADMIN."""
    CourseService.delete_course(db, course_id)


@router.post("/{course_id}/prerequisites", response_model=CoursePrerequisiteResponse, status_code=201)
def add_prerequisite(
    course_id: str,
    data: CoursePrerequisiteCreate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Thêm môn tiên quyết. Chỉ ADMIN."""
    return CourseService.add_prerequisite(db, course_id, data.prerequisite_course_id)


@router.delete("/{course_id}/prerequisites/{prereq_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_prerequisite(course_id: str, prereq_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Gỡ môn tiên quyết. Chỉ ADMIN."""
    CourseService.remove_prerequisite(db, course_id, prereq_id)
