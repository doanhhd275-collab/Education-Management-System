"""
services/class_service.py — Business logic cho Class management
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.class_ import Class, TeacherClass
from app.models.teacher import Teacher
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student


class ClassService:

    @staticmethod
    def list_classes(db: Session, course_id: str | None = None,
                     semester: str | None = None,
                     page: int = 1, page_size: int = 20) -> list[Class]:
        query = db.query(Class)
        if course_id:
            query = query.filter(Class.course_id == course_id)
        if semester:
            query = query.filter(Class.semester == semester)
        return query.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def create_class(db: Session, course_id: str, class_id: str,
                     semester: str | None = None, capacity: int | None = None,
                     day_of_week: str | None = None, start_period: int | None = None,
                     end_period: int | None = None) -> Class:
        if not db.query(Course).filter(Course.course_id == course_id).first():
            raise HTTPException(status_code=404, detail=f"Không tìm thấy môn học '{course_id}'")
        if db.query(Class).filter(Class.course_id == course_id, Class.class_id == class_id).first():
            raise HTTPException(status_code=400, detail=f"Lớp '{class_id}' của môn '{course_id}' đã tồn tại")

        new_class = Class(
            course_id=course_id, class_id=class_id,
            semester=semester, capacity=capacity,
            day_of_week=day_of_week, start_period=start_period, end_period=end_period,
        )
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        return new_class

    @staticmethod
    def get_class(db: Session, course_id: str, class_id: str) -> Class:
        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        return class_

    @staticmethod
    def update_class(db: Session, course_id: str, class_id: str, update_data: dict) -> Class:
        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        for field, value in update_data.items():
            setattr(class_, field, value)
        db.commit()
        db.refresh(class_)
        return class_

    @staticmethod
    def delete_class(db: Session, course_id: str, class_id: str) -> None:
        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        db.delete(class_)
        db.commit()

    @staticmethod
    def assign_teacher(db: Session, course_id: str, class_id: str,
                       teacher_id: str, semester: str) -> TeacherClass:
        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        if not db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
        if db.query(TeacherClass).filter(
            TeacherClass.teacher_id == teacher_id,
            TeacherClass.class_id == class_id,
            TeacherClass.semester == semester
        ).first():
            raise HTTPException(status_code=400, detail="Giáo viên đã được gán vào lớp này rồi")

        tc = TeacherClass(teacher_id=teacher_id, semester=semester, class_id=class_id, course_id=course_id)
        db.add(tc)
        db.commit()
        db.refresh(tc)
        return tc

    @staticmethod
    def get_students(db: Session, course_id: str, class_id: str) -> list[dict]:
        """Lấy danh sách sinh viên trong lớp kèm điểm số."""
        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

        enrollments = (
            db.query(Enrollment)
            .options(joinedload(Enrollment.student).joinedload(Student.user))
            .filter(Enrollment.course_id == course_id, Enrollment.class_id == class_id)
            .all()
        )
        return [
            {
                "student_id":       e.student_id,
                "student_name":     e.student.user.name if e.student and e.student.user else "N/A",
                "midterm_score":    e.midterm_score,
                "final_term_score": e.final_term_score,
                "grade":            e.grade,
                "status":           e.status,
            }
            for e in enrollments
        ]
