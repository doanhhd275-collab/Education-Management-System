"""
services/student_service.py — Business logic cho Student management
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.student import Student


class StudentService:

    @staticmethod
    def list_students(db: Session, program_id: str | None = None,
                      page: int = 1, page_size: int = 20) -> list[Student]:
        query = db.query(Student).options(joinedload(Student.user))
        if program_id:
            query = query.filter(Student.program_id == program_id)
        return query.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def get_student(db: Session, user_id: str) -> Student:
        student = (
            db.query(Student)
            .options(joinedload(Student.user))
            .filter(Student.user_id == user_id)
            .first()
        )
        if not student:
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
        return student

    @staticmethod
    def update_student(db: Session, user_id: str, update_data: dict) -> Student:
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
        for field, value in update_data.items():
            setattr(student, field, value)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def get_enrollments(db: Session, user_id: str) -> list:
        """Lấy danh sách lớp học + điểm số của sinh viên."""
        from app.models.enrollment import Enrollment
        enrollments = db.query(Enrollment).filter(Enrollment.student_id == user_id).all()
        return [
            {
                "class_id":         e.class_id,
                "course_id":        e.course_id,
                "midterm_score":    e.midterm_score,
                "final_term_score": e.final_term_score,
                "grade":            e.grade,
                "status":           e.status,
            }
            for e in enrollments
        ]
