"""
services/attendance_service.py — Business logic cho Điểm danh (LessonReport)
"""
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.attendance import LessonReport


class AttendanceService:

    @staticmethod
    def mark_attendance(db: Session, records: list) -> list[LessonReport]:
        """
        Điểm danh nhiều sinh viên cùng lúc (bulk upsert).
        Nếu đã tồn tại thì cập nhật, chưa có thì tạo mới.
        """
        created = []
        for record in records:
            existing = db.query(LessonReport).filter(
                LessonReport.class_id   == record.class_id,
                LessonReport.day        == record.day,
                LessonReport.student_id == record.student_id,
                LessonReport.lesson_id  == record.lesson_id,
            ).first()

            if existing:
                existing.absent = record.absent
                existing.submit_assignment_status = record.submit_assignment_status
                created.append(existing)
            else:
                new_record = LessonReport(
                    class_id=record.class_id,
                    course_id=record.course_id,
                    day=record.day,
                    student_id=record.student_id,
                    lesson_id=record.lesson_id,
                    absent=record.absent,
                    submit_assignment_status=record.submit_assignment_status,
                )
                db.add(new_record)
                created.append(new_record)

        db.commit()
        for r in created:
            db.refresh(r)
        return created

    @staticmethod
    def get_attendance(
        db: Session,
        current_user,
        class_id: str | None = None,
        course_id: str | None = None,
        student_id: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[LessonReport]:
        query = db.query(LessonReport)

        role_ids = [ur.role_id for ur in current_user.user_roles]
        is_student_only = "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids

        if is_student_only:
            query = query.filter(LessonReport.student_id == current_user.user_id)
        else:
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

    @staticmethod
    def update_attendance(
        db: Session,
        class_id: str, day: datetime, student_id: str, lesson_id: str,
        update_data: dict,
    ) -> LessonReport:
        record = db.query(LessonReport).filter(
            LessonReport.class_id   == class_id,
            LessonReport.day        == day,
            LessonReport.student_id == student_id,
            LessonReport.lesson_id  == lesson_id,
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi điểm danh")

        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record
