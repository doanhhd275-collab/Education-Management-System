"""
services/timetable_service.py — Business logic cho Thời khóa biểu

Tách riêng khỏi class_service vì đây là query phức tạp
kết hợp nhiều models (Teacher, TeacherClass, Class, Course, Enrollment, Student).
"""
from sqlalchemy.orm import Session

from app.models.class_ import Class, TeacherClass
from app.models.teacher import Teacher
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student


class TimetableService:

    @staticmethod
    def get_teacher_timetable(db: Session, user_id: str) -> list[dict]:
        """Trả về thời khóa biểu của giáo viên đang đăng nhập."""
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if not teacher:
            return []

        tcs = db.query(TeacherClass).filter(TeacherClass.teacher_id == teacher.teacher_id).all()

        result = []
        for tc in tcs:
            cls = db.query(Class).filter(
                Class.course_id == tc.course_id,
                Class.class_id  == tc.class_id
            ).first()
            if not cls:
                continue
            course = db.query(Course).filter(Course.course_id == cls.course_id).first()
            result.append({
                "class_id":     cls.class_id,
                "course_id":    cls.course_id,
                "course_name":  course.course_name if course else cls.course_id,
                "semester":     cls.semester or tc.semester,
                "capacity":     cls.capacity,
                "day_of_week":  cls.day_of_week,
                "start_period": cls.start_period,
                "end_period":   cls.end_period,
                "room":         getattr(cls, "room", None),
            })
        return result

    @staticmethod
    def get_student_timetable(db: Session, user_id: str) -> list[dict]:
        """Trả về thời khóa biểu của sinh viên đang đăng nhập."""
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            return []

        enrollments_list = db.query(Enrollment).filter(
            Enrollment.student_id == student.user_id
        ).all()

        result = []
        for e in enrollments_list:
            cls = db.query(Class).filter(
                Class.course_id == e.course_id,
                Class.class_id  == e.class_id
            ).first()
            if not cls:
                continue
            course = db.query(Course).filter(Course.course_id == cls.course_id).first()
            result.append({
                "class_id":     cls.class_id,
                "course_id":    cls.course_id,
                "course_name":  course.course_name if course else cls.course_id,
                "semester":     cls.semester,
                "capacity":     cls.capacity,
                "day_of_week":  cls.day_of_week,
                "start_period": cls.start_period,
                "end_period":   cls.end_period,
                "room":         getattr(cls, "room", None),
            })
        return result
