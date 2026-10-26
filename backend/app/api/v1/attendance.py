"""
Router: Điểm danh (Attendance / LessonReport)
Endpoints:
  POST /api/v1/attendance                                                    — TEACHER: điểm danh bulk
  GET  /api/v1/attendance                                                    — Xem điểm danh
  PUT  /api/v1/attendance/{class_id}/{day}/{student_id}/{lesson_id}          — TEACHER: cập nhật
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.assignment import LessonReportCreate, LessonReportUpdate, LessonReportResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Điểm danh"])


@router.post("", response_model=list[LessonReportResponse], status_code=201)
def mark_attendance(
    records: list[LessonReportCreate],
    db: DbDep = None,
    _=Depends(require_role("TEACHER")),
):
    """Điểm danh nhiều sinh viên cùng lúc (bulk). Chỉ TEACHER."""
    return AttendanceService.mark_attendance(db, records)


@router.get("", response_model=list[LessonReportResponse])
def get_attendance(
    class_id: str | None    = Query(None),
    course_id: str | None   = Query(None),
    student_id: str | None  = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None   = Query(None),
    db: DbDep = None,
    current_user: CurrentUserDep = None,
):
    """Xem lịch sử điểm danh — STUDENT chỉ thấy của mình."""
    return AttendanceService.get_attendance(db, current_user, class_id, course_id, student_id, from_date, to_date)


@router.put("/{class_id}/{day}/{student_id}/{lesson_id}", response_model=LessonReportResponse)
def update_attendance(
    class_id: str,
    day: datetime,
    student_id: str,
    lesson_id: str,
    data: LessonReportUpdate,
    db: DbDep = None,
    _=Depends(require_role("TEACHER")),
):
    """Cập nhật trạng thái điểm danh. Chỉ TEACHER."""
    return AttendanceService.update_attendance(db, class_id, day, student_id, lesson_id, data.model_dump(exclude_none=True))
