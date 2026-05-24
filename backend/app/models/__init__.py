"""
Import tất cả models để SQLAlchemy/Alembic nhận diện và tạo bảng đúng thứ tự.
"""
from app.models.base import Base          # noqa: F401
from app.models.user import (             # noqa: F401
    User, Role, UserRole,
    Student, Teacher,
    Curriculum, Course, CurriculumCourse, CoursePrerequisite,
    Class, CourseTeacher, TeacherClass,
    Enrollment,
    Assignment, AssignmentReport, LessonReport,
    Document,
    ReportLog, SystemLog,
)
