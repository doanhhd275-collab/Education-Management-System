"""
Router: Quản lý lớp học (Classes) + Thời khóa biểu
Endpoints:
  GET    /api/v1/classes                                      — Danh sách lớp
  POST   /api/v1/classes                                      — ADMIN: tạo lớp
  GET    /api/v1/classes/timetable/teacher                    — TKB giáo viên
  GET    /api/v1/classes/timetable/student                    — TKB sinh viên
  GET    /api/v1/classes/{course_id}/{class_id}               — Chi tiết lớp
  PUT    /api/v1/classes/{course_id}/{class_id}               — ADMIN: cập nhật
  DELETE /api/v1/classes/{course_id}/{class_id}               — ADMIN: xóa
  POST   /api/v1/classes/{course_id}/{class_id}/teachers      — ADMIN: gán giáo viên
  GET    /api/v1/classes/{course_id}/{class_id}/students      — Danh sách sinh viên trong lớp
"""
import logging
import traceback as tb

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.class_ import (
    ClassCreate, ClassUpdate, ClassResponse,
    TeacherClassCreate, TeacherClassResponse,
)
from app.services.class_service import ClassService
from app.services.timetable_service import TimetableService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/classes", tags=["Lớp học"])


@router.get("", response_model=list[ClassResponse])
def list_classes(
    course_id: str | None = Query(None),
    semester: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbDep = None,
    _: CurrentUserDep = None,
):
    """Lấy danh sách lớp học."""
    return ClassService.list_classes(db, course_id, semester, page, page_size)


@router.post("", response_model=ClassResponse, status_code=201)
def create_class(data: ClassCreate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Tạo lớp học mới. Chỉ ADMIN."""
    return ClassService.create_class(
        db, data.course_id, data.class_id,
        data.semester, data.capacity,
        data.day_of_week, data.start_period, data.end_period,
    )


# ── Timetable routes (phải đứng TRƯỚC /{course_id}/... để không bị che) ──

@router.get("/timetable/teacher", tags=["Thời khóa biểu"])
def teacher_timetable(db: DbDep = None, current_user: CurrentUserDep = None):
    """Trả về thời khóa biểu của giáo viên đang đăng nhập."""
    return TimetableService.get_teacher_timetable(db, current_user.user_id)


@router.get("/timetable/student", tags=["Thời khóa biểu"])
def student_timetable(db: DbDep = None, current_user: CurrentUserDep = None):
    """Trả về thời khóa biểu của sinh viên đang đăng nhập."""
    try:
        return TimetableService.get_student_timetable(db, current_user.user_id)
    except Exception as exc:
        logger.error("student_timetable error: %s\n%s", exc, tb.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))


# ── CRUD routes ────────────────────────────────────────────

@router.get("/{course_id}/{class_id}", response_model=ClassResponse)
def get_class(course_id: str, class_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem chi tiết lớp học."""
    return ClassService.get_class(db, course_id, class_id)


@router.put("/{course_id}/{class_id}", response_model=ClassResponse)
def update_class(
    course_id: str, class_id: str,
    data: ClassUpdate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Cập nhật thông tin lớp học. Chỉ ADMIN."""
    return ClassService.update_class(db, course_id, class_id, data.model_dump())


@router.delete("/{course_id}/{class_id}", status_code=204)
def delete_class(course_id: str, class_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Xóa lớp học. Chỉ ADMIN."""
    ClassService.delete_class(db, course_id, class_id)


@router.post("/{course_id}/{class_id}/teachers", response_model=TeacherClassResponse, status_code=201)
def assign_teacher(
    course_id: str, class_id: str,
    data: TeacherClassCreate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Gán giáo viên dạy lớp. Chỉ ADMIN."""
    return ClassService.assign_teacher(db, course_id, class_id, data.teacher_id, data.semester)


@router.get("/{course_id}/{class_id}/students")
def get_class_students(
    course_id: str, class_id: str,
    db: DbDep = None,
    _=Depends(require_role("ADMIN", "TEACHER")),
):
    """Lấy danh sách sinh viên trong lớp kèm điểm số. ADMIN và TEACHER."""
    return ClassService.get_students(db, course_id, class_id)
