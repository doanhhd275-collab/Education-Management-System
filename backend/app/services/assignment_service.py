"""
services/assignment_service.py — Business logic cho Assignments + AssignmentReports
"""
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment, AssignmentReport
from app.models.student import Student


class AssignmentService:

    # ── Assignments ─────────────────────────────────────────────

    @staticmethod
    def list_assignments(db: Session, class_id: str | None = None,
                         course_id: str | None = None) -> list[Assignment]:
        query = db.query(Assignment)
        if class_id:
            query = query.filter(Assignment.class_id == class_id)
        if course_id:
            query = query.filter(Assignment.course_id == course_id)
        return query.all()

    @staticmethod
    def create_assignment(db: Session, assignment_id: str, assignment_name: str,
                          deadline, class_id: str, course_id: str,
                          teacher_id: str | None = None, semester: str | None = None,
                          link_url: str | None = None) -> Assignment:
        if db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first():
            raise HTTPException(status_code=400, detail=f"AssignmentID '{assignment_id}' đã tồn tại")

        assignment = Assignment(
            assignment_id=assignment_id, assignment_name=assignment_name,
            deadline=deadline, class_id=class_id, course_id=course_id,
            teacher_id=teacher_id, semester=semester, link_url=link_url,
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_assignment(db: Session, assignment_id: str) -> Assignment:
        assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
        return assignment

    @staticmethod
    def update_assignment(db: Session, assignment_id: str, update_data: dict) -> Assignment:
        assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
        for field, value in update_data.items():
            setattr(assignment, field, value)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def delete_assignment(db: Session, assignment_id: str) -> None:
        assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
        db.delete(assignment)
        db.commit()

    # ── Submissions (AssignmentReport) ──────────────────────────

    @staticmethod
    def get_reports(db: Session, assignment_id: str) -> list[dict]:
        """Xem tất cả bài nộp của một bài tập kèm thông tin sinh viên."""
        if not db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")

        reports = (
            db.query(AssignmentReport)
            .options(joinedload(AssignmentReport.student).joinedload(Student.user))
            .filter(AssignmentReport.assignment_id == assignment_id)
            .all()
        )

        result = []
        for r in reports:
            student_name = r.student.user.name if r.student and r.student.user else None
            deadline = r.assignment.deadline if r.assignment else None
            is_late = bool(
                deadline and r.submit_date
                and r.submit_date.replace(tzinfo=None) > deadline.replace(tzinfo=None)
            ) if r.submit_date else None
            result.append({
                "assignment_id": r.assignment_id,
                "student_id":    r.student_id,
                "student_name":  student_name,
                "class_id":      r.class_id,
                "lesson_id":     r.lesson_id,
                "submit_date":   r.submit_date,
                "link_url":      r.link_url,
                "grade":         r.grade,
                "feedback":      r.feedback,
                "is_late":       is_late,
            })
        return result

    @staticmethod
    def get_my_submissions(db: Session, user_id: str) -> list[dict]:
        """Sinh viên xem tất cả bài nộp của mình kèm điểm."""
        reports = db.query(AssignmentReport).filter(AssignmentReport.student_id == user_id).all()
        return [
            {
                "assignment_id":   r.assignment_id,
                "assignment_name": r.assignment.assignment_name if r.assignment else r.assignment_id,
                "course_id":       r.assignment.course_id if r.assignment else None,
                "class_id":        r.class_id,
                "submit_date":     r.submit_date,
                "link_url":        r.link_url,
                "grade":           r.grade,
                "feedback":        r.feedback,
            }
            for r in reports
        ]

    @staticmethod
    def submit(db: Session, current_user, assignment_id: str,
               student_id: str, class_id: str, lesson_id: str | None,
               link_url: str | None, submit_date=None) -> dict:
        """Sinh viên nộp bài (hoặc nộp lại)."""
        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "STUDENT" in role_ids and "ADMIN" not in role_ids:
            if student_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Bạn chỉ được nộp bài cho bản thân")

        assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")

        now = submit_date or datetime.now(timezone.utc)

        existing = db.query(AssignmentReport).filter(
            AssignmentReport.assignment_id == assignment_id,
            AssignmentReport.student_id    == student_id,
        ).first()

        if existing:
            existing.link_url    = link_url
            existing.submit_date = now
            db.commit()
            db.refresh(existing)
            r = existing
        else:
            r = AssignmentReport(
                assignment_id=assignment_id, class_id=class_id,
                student_id=student_id, lesson_id=lesson_id,
                link_url=link_url, submit_date=now,
            )
            db.add(r)
            db.commit()
            db.refresh(r)

        deadline = assignment.deadline
        sub_dt   = r.submit_date
        is_late  = bool(deadline and sub_dt and sub_dt.replace(tzinfo=None) > deadline.replace(tzinfo=None))

        return {
            "assignment_id": r.assignment_id,
            "student_id":    r.student_id,
            "student_name":  None,
            "class_id":      r.class_id,
            "lesson_id":     r.lesson_id,
            "submit_date":   r.submit_date,
            "link_url":      r.link_url,
            "grade":         r.grade,
            "feedback":      r.feedback,
            "is_late":       is_late,
        }

    @staticmethod
    def grade_submission(db: Session, assignment_id: str, student_id: str,
                         grade: float, feedback: str | None) -> dict:
        report = db.query(AssignmentReport).filter(
            AssignmentReport.assignment_id == assignment_id,
            AssignmentReport.student_id    == student_id,
        ).first()
        if not report:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài nộp")
        report.grade    = grade
        report.feedback = feedback
        db.commit()
        db.refresh(report)
        return {"message": "Đã chấm điểm", "grade": report.grade, "feedback": report.feedback}
