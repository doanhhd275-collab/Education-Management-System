"""
Router: Điểm danh (Attendance / LessonReport)
Giáo viên điểm danh từng buổi học, sinh viên xem lịch sử vắng mặt.

Endpoints:
  POST /api/v1/attendance        — TEACHER: điểm danh một loạt sinh viên (bulk)
  GET  /api/v1/attendance        — Xem điểm danh (filter theo class, student, ngày)
  PUT  /api/v1/attendance/{class_id}/{day}/{student_id}/{lesson_id}  — TEACHER: cập nhật
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import LessonReport, Class, User
from app.schemas.assignment import LessonReportCreate, LessonReportUpdate, LessonReportResponse

router = APIRouter(prefix="/attendance", tags=["Điểm danh"])


@router.post("", response_model=list[LessonReportResponse], status_code=status.HTTP_201_CREATED)
def mark_attendance(
    records: list[LessonReportCreate],
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """
    Điểm danh nhiều sinh viên cùng lúc (bulk insert).
    Truyền vào một danh sách các bản ghi điểm danh.
    Chỉ TEACHER và ADMIN.
    """
    created = []
    for record in records:
        # Kiểm tra đã điểm danh buổi này chưa
        existing = db.query(LessonReport).filter(
            LessonReport.class_id  == record.class_id,
            LessonReport.day       == record.day,
            LessonReport.student_id == record.student_id,
            LessonReport.lesson_id == record.lesson_id
        ).first()

        if existing:
            # Nếu đã có thì cập nhật thay vì báo lỗi
            existing.absent = record.absent
            existing.submit_assignment_status = record.submit_assignment_status
            created.append(existing)
        else:
            # Tạo mới
            new_record = LessonReport(
                class_id=record.class_id,
                course_id=record.course_id,
                day=record.day,
                student_id=record.student_id,
                lesson_id=record.lesson_id,
                absent=record.absent,
                submit_assignment_status=record.submit_assignment_status
            )
            db.add(new_record)
            created.append(new_record)

    db.commit()
    for r in created:
        db.refresh(r)
    return created


@router.get("", response_model=list[LessonReportResponse])
def get_attendance(
    class_id: str | None    = Query(None, description="Lọc theo lớp"),
    course_id: str | None   = Query(None, description="Lọc theo môn"),
    student_id: str | None  = Query(None, description="Lọc theo sinh viên (chỉ TEACHER/ADMIN)"),
    from_date: datetime | None = Query(None, description="Từ ngày (ISO format)"),
    to_date: datetime | None   = Query(None, description="Đến ngày (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xem lịch sử điểm danh.
    - STUDENT: tự động lọc theo mình (chỉ xem của bản thân, không thể lọc người khác)
    - TEACHER/ADMIN: lọc tùy ý theo student_id, class_id, course_id, ngày
    """
    query = db.query(LessonReport)

    # Lấy danh sách role của user hiện tại
    role_ids = [ur.role_id for ur in current_user.user_roles]
    is_student_only = "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids

    if is_student_only:
        # Sinh viên chỉ xem được điểm danh của chính mình — bỏ qua student_id từ query param
        query = query.filter(LessonReport.student_id == current_user.user_id)
    else:
        # TEACHER / ADMIN: lọc theo student_id nếu truyền vào
        if student_id:
            query = query.filter(LessonReport.student_id == student_id)

    if class_id:
        query = query.filter(LessonReport.class_id == class_id)
    if course_id:
        query = query.filter(LessonReport.course_id == course_id)
    if from_date:
        query = query.filter(LessonReport.day >= from_date)
    if to_date:
        query = query.filter(LessonReport.day <= to_date)

    return query.order_by(LessonReport.day.desc()).all()


@router.put("/{class_id}/{day}/{student_id}/{lesson_id}", response_model=LessonReportResponse)
def update_attendance(
    class_id: str,
    day: datetime,
    student_id: str,
    lesson_id: str,
    data: LessonReportUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """Cập nhật trạng thái điểm danh cho một sinh viên cụ thể. TEACHER và ADMIN."""
    record = db.query(LessonReport).filter(
        LessonReport.class_id   == class_id,
        LessonReport.day        == day,
        LessonReport.student_id == student_id,
        LessonReport.lesson_id  == lesson_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi điểm danh")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record
