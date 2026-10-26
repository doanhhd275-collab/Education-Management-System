"""
models/__init__.py

Import tất cả ORM models theo thứ tự dependency để SQLAlchemy mapper
hoàn chỉnh trước khi relationships được resolve.

Thứ tự quan trọng:
  1. Base (declarative base)
  2. User, Role (không phụ thuộc model nào)
  3. Curriculum, Course (phụ thuộc nhau qua junction)
  4. Teacher, Student (phụ thuộc User, Curriculum, Course)
  5. Class, TeacherClass (phụ thuộc Course, Teacher)
  6. Enrollment (phụ thuộc Class, Student)
  7. Assignment, AssignmentReport (phụ thuộc Class, TeacherClass, Student)
  8. LessonReport / Attendance (phụ thuộc Class, Student)
  9. Document (phụ thuộc Teacher)
  10. Log (phụ thuộc User)
"""
from app.models.base import Base                      # noqa: F401

# Tier 1 — Auth
from app.models.user import Role, User, UserRole      # noqa: F401

# Tier 2 — Programs & Courses (no Student/Teacher dependency)
from app.models.curriculum import Curriculum, CurriculumCourse   # noqa: F401
from app.models.course import Course, CoursePrerequisite         # noqa: F401

# Tier 3 — People profiles
from app.models.student import Student                # noqa: F401
from app.models.teacher import Teacher, CourseTeacher # noqa: F401

# Tier 4 — Classes
from app.models.class_ import Class, TeacherClass     # noqa: F401

# Tier 5 — Enrollment
from app.models.enrollment import Enrollment          # noqa: F401

# Tier 6 — Assignments & Attendance
from app.models.assignment import Assignment, AssignmentReport   # noqa: F401
from app.models.attendance import LessonReport                   # noqa: F401

# Tier 7 — Documents
from app.models.document import Document              # noqa: F401

# Tier 8 — Logging
from app.models.log import ReportLog, SystemLog       # noqa: F401

__all__ = [
    "Base",
    # Auth
    "Role", "User", "UserRole",
    # Programs & Courses
    "Curriculum", "CurriculumCourse",
    "Course", "CoursePrerequisite",
    # People
    "Student",
    "Teacher", "CourseTeacher",
    # Classes
    "Class", "TeacherClass",
    # Enrollment
    "Enrollment",
    # Assignments & Attendance
    "Assignment", "AssignmentReport",
    "LessonReport",
    # Documents
    "Document",
    # Logs
    "ReportLog", "SystemLog",
]
