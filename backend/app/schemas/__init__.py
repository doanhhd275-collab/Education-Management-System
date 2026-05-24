"""
Schemas package – re-export tất cả schemas để import tiện hơn.

Cách dùng:
    from app.schemas import UserCreate, UserResponse, EnrollmentResponse
"""

# User & Auth
from app.schemas.user import (
    RoleCreate, RoleResponse,
    UserBase, UserCreate, UserUpdate, UserResponse,
    UserRoleCreate, UserRoleResponse,
    StudentCreate, StudentUpdate, StudentResponse,
    TeacherCreate, TeacherResponse,
)

# Curriculum & Course
from app.schemas.curriculum import (
    CurriculumCreate, CurriculumUpdate, CurriculumResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    CurriculumCourseCreate, CurriculumCourseResponse,
    CoursePrerequisiteCreate, CoursePrerequisiteResponse,
)

# Class
from app.schemas.class_ import (
    ClassCreate, ClassUpdate, ClassResponse,
    CourseTeacherCreate, CourseTeacherResponse,
    TeacherClassCreate, TeacherClassResponse,
)

# Enrollment
from app.schemas.enrollment import (
    EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse,
    EnrollmentListFilter,
)

# Assignment & Reports
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentReportCreate, AssignmentReportResponse,
    LessonReportCreate, LessonReportUpdate, LessonReportResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
)

# Logs
from app.schemas.log import (
    ReportLogCreate, ReportLogResponse, ReportLogFilter,
    SystemLogCreate, SystemLogResponse, SystemLogFilter,
)

__all__ = [
    # User & Auth
    "RoleCreate", "RoleResponse",
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "UserRoleCreate", "UserRoleResponse",
    "StudentCreate", "StudentUpdate", "StudentResponse",
    "TeacherCreate", "TeacherResponse",
    # Curriculum & Course
    "CurriculumCreate", "CurriculumUpdate", "CurriculumResponse",
    "CourseCreate", "CourseUpdate", "CourseResponse",
    "CurriculumCourseCreate", "CurriculumCourseResponse",
    "CoursePrerequisiteCreate", "CoursePrerequisiteResponse",
    # Class
    "ClassCreate", "ClassUpdate", "ClassResponse",
    "CourseTeacherCreate", "CourseTeacherResponse",
    "TeacherClassCreate", "TeacherClassResponse",
    # Enrollment
    "EnrollmentCreate", "EnrollmentUpdate", "EnrollmentResponse",
    "EnrollmentListFilter",
    # Assignment & Reports
    "AssignmentCreate", "AssignmentUpdate", "AssignmentResponse",
    "AssignmentReportCreate", "AssignmentReportResponse",
    "LessonReportCreate", "LessonReportUpdate", "LessonReportResponse",
    "DocumentCreate", "DocumentUpdate", "DocumentResponse",
    # Logs
    "ReportLogCreate", "ReportLogResponse", "ReportLogFilter",
    "SystemLogCreate", "SystemLogResponse", "SystemLogFilter",
]
