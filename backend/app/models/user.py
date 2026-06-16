from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, ForeignKey, ForeignKeyConstraint,
    PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship

from app.models.base import Base


# ============================================================
# SECTION 1: USER & AUTH
# ============================================================

class Role(Base):
    __tablename__ = "roles"

    role_id   = Column("RoleID",   String(10), primary_key=True)
    role_name = Column("RoleName", String(30), nullable=False)

    # relationships
    user_roles = relationship("UserRole", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id   = Column("UserID",   String(10), primary_key=True)
    email     = Column("Email",    String(50), nullable=False, unique=True)
    password  = Column("Password", String(255), nullable=False)  # bcrypt hash dài ~60 ký tự
    contact   = Column("Contact",  String(15))
    birth     = Column("BirthDate", DateTime)           # DATE per ERD
    name      = Column("Name",     String(30), nullable=False)

    # relationships
    user_roles  = relationship("UserRole",  back_populates="user")
    student     = relationship("Student",   back_populates="user", uselist=False)
    teacher     = relationship("Teacher",   back_populates="user", uselist=False)
    report_logs = relationship("ReportLog", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")


class UserRole(Base):
    """Junction table: User ↔ Role (Many-to-Many)."""
    __tablename__ = "user_roles"

    user_id = Column("UserID", String(10), ForeignKey("users.UserID"),  primary_key=True)
    role_id = Column("RoleID", String(10), ForeignKey("roles.RoleID"),  primary_key=True)

    # relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


# ============================================================
# SECTION 2: STUDENT & TEACHER  (profile extensions of User)
# ============================================================

class Student(Base):
    """
    Mỗi User chỉ là sinh viên của 1 chương trình (đơn giản cho project học thuật).
    PK = UserID (single) để Enrollment có thể FK vào students.UserID.
    """
    __tablename__ = "students"

    user_id              = Column("UserID",              String(10), ForeignKey("users.UserID"), primary_key=True)
    program_id           = Column("ProgramID",           String(10), ForeignKey("curriculums.ProgramID"), nullable=True)
    cpa                  = Column("CPA",                 Float)
    gpa                  = Column("GPA",                 Float)
    warning_level        = Column("WarningLevel",        Integer, default=0)
    graduation_condition = Column("GraduationCondition", Boolean, default=False)

    # relationships
    user              = relationship("User",             back_populates="student")
    program           = relationship("Curriculum",       back_populates="students")
    enrollments       = relationship("Enrollment",       back_populates="student",
                                     foreign_keys="[Enrollment.student_id]")
    assignment_reports = relationship("AssignmentReport", back_populates="student",
                                      foreign_keys="[AssignmentReport.student_id]")
    lesson_reports    = relationship("LessonReport",     back_populates="student",
                                     foreign_keys="[LessonReport.student_id]")


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column("TeacherID", String(10), primary_key=True)
    user_id    = Column("UserID",    String(10), ForeignKey("users.UserID"), unique=True)

    # relationships
    user            = relationship("User",          back_populates="teacher")
    course_teachers = relationship("CourseTeacher", back_populates="teacher")
    teacher_classes = relationship("TeacherClass",  back_populates="teacher")
    documents       = relationship("Document",      back_populates="teacher")


# ============================================================
# SECTION 3: CURRICULUM & COURSE
# ============================================================

class Curriculum(Base):
    """Chương trình đào tạo – tên bảng theo ERD: Curriculum."""
    __tablename__ = "curriculums"

    program_id   = Column("ProgramID",   String(10), primary_key=True)
    program_name = Column("ProgramName", String(30), nullable=False)

    # relationships
    students          = relationship("Student",          back_populates="program")
    curriculum_courses = relationship("CurriculumCourse", back_populates="curriculum")


class Course(Base):
    __tablename__ = "courses"

    course_id   = Column("CourseID",   String(10), primary_key=True)
    course_name = Column("CourseName", String(30), nullable=False)

    # relationships
    classes           = relationship("Class",            back_populates="course")
    curriculum_courses = relationship("CurriculumCourse", back_populates="course")
    course_teachers   = relationship("CourseTeacher",    back_populates="course")
    # self-referencing: môn này YÊU CẦU các môn tiên quyết
    prerequisites_of  = relationship(
        "CoursePrerequisite",
        foreign_keys="[CoursePrerequisite.course_id]",
        back_populates="course",
        lazy="select"
    )
    # self-referencing: môn này LÀ tiên quyết của các môn khác
    required_by       = relationship(
        "CoursePrerequisite",
        foreign_keys="[CoursePrerequisite.prerequisite_course_id]",
        back_populates="prerequisite_course"
    )

    @property
    def prerequisites(self):
        """Alias cho prerequisites_of – dùng để CourseResponse serialize đúng field name."""
        return self.prerequisites_of


class CurriculumCourse(Base):
    """Junction table: Curriculum ↔ Course (Many-to-Many)."""
    __tablename__ = "curriculum_courses"

    program_id = Column("ProgramID", String(10), ForeignKey("curriculums.ProgramID"), primary_key=True)
    course_id  = Column("CourseID",  String(10), ForeignKey("courses.CourseID"),       primary_key=True)

    # relationships
    curriculum = relationship("Curriculum", back_populates="curriculum_courses")
    course     = relationship("Course",     back_populates="curriculum_courses")


class CoursePrerequisite(Base):
    """Self-referencing: một Course có thể có nhiều môn tiên quyết."""
    __tablename__ = "course_prerequisites"

    course_id              = Column("CourseID",             String(10), ForeignKey("courses.CourseID"), primary_key=True)
    prerequisite_course_id = Column("PrerequisiteCourseID", String(10), ForeignKey("courses.CourseID"), primary_key=True)

    # relationships
    course             = relationship("Course", foreign_keys=[course_id],              back_populates="prerequisites_of")
    prerequisite_course = relationship("Course", foreign_keys=[prerequisite_course_id], back_populates="required_by")

    @property
    def prerequisite_course_name(self) -> str | None:
        """Tên môn tiên quyết – dùng để serialize trong CoursePrerequisiteResponse."""
        return self.prerequisite_course.course_name if self.prerequisite_course else None


# ============================================================
# SECTION 4: CLASS
# ============================================================

class Class(Base):
    """
    ERD: PK = (CourseID, ClassID)  – composite primary key.
    Capacity thay cho NumberOfStudent.
    """
    __tablename__ = "classes"

    course_id    = Column("CourseID",    String(10), ForeignKey("courses.CourseID"), nullable=False)
    class_id     = Column("ClassID",     String(10), nullable=False)
    semester     = Column("Semester",    String(10))
    capacity     = Column("Capacity",    Integer)              # ERD: Capacity INT
    day_of_week  = Column("DayOfWeek",   String(5))            # "2".."7" (Thứ 2-7)
    start_period = Column("StartPeriod", Integer)              # 1-12
    end_period   = Column("EndPeriod",   Integer)              # 1-12
    room         = Column("Room",        String(20))           # Phòng học (VD: B1-301)

    __table_args__ = (
        PrimaryKeyConstraint("CourseID", "ClassID"),
    )

    # relationships
    course          = relationship("Course",       back_populates="classes")
    teacher_classes = relationship("TeacherClass", back_populates="class_")
    enrollments     = relationship("Enrollment",   back_populates="class_")
    assignments     = relationship("Assignment",   back_populates="class_")
    lesson_reports  = relationship("LessonReport", back_populates="class_")


class CourseTeacher(Base):
    """Junction table: Course ↔ Teacher (Many-to-Many)."""
    __tablename__ = "course_teachers"

    course_id  = Column("CourseID",  String(10), ForeignKey("courses.CourseID"),   primary_key=True)
    teacher_id = Column("TeacherID", String(10), ForeignKey("teachers.TeacherID"), primary_key=True)

    # relationships
    course  = relationship("Course",  back_populates="course_teachers")
    teacher = relationship("Teacher", back_populates="course_teachers")


class TeacherClass(Base):
    """
    ERD: PK = (TeacherID, Semester, ClassID).
    FK ClassID+CourseID → classes(CourseID, ClassID).
    """
    __tablename__ = "teacher_classes"

    teacher_id = Column("TeacherID", String(10), ForeignKey("teachers.TeacherID"), nullable=False)
    semester   = Column("Semester",  String(10), nullable=False)
    class_id   = Column("ClassID",   String(10), nullable=False)
    course_id  = Column("CourseID",  String(10), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("TeacherID", "Semester", "ClassID"),
        ForeignKeyConstraint(
            ["CourseID", "ClassID"],
            ["classes.CourseID", "classes.ClassID"]
        ),
    )

    # relationships
    teacher    = relationship("Teacher", back_populates="teacher_classes")
    class_     = relationship("Class",   back_populates="teacher_classes")
    assignments = relationship("Assignment", back_populates="teacher_class",
                               overlaps="assignments,class_")


# ============================================================
# SECTION 5: ENROLLMENT
# ============================================================

class Enrollment(Base):
    """
    ERD: PK = (ClassID, StudentID).
    FK ClassID+CourseID → classes composite PK.
    FK StudentID        → students.UserID (part of student PK).
    """
    __tablename__ = "enrollments"

    class_id         = Column("ClassID",        String(10), nullable=False)
    course_id        = Column("CourseID",        String(10), nullable=False)
    student_id       = Column("StudentID",       String(10), nullable=False)
    midterm_score    = Column("MidTermScore",    Float)
    final_term_score = Column("FinalTermScore",  Float)
    grade            = Column("Grade",           String(1))   # CHAR(1)
    status           = Column("Status",          String(10))

    __table_args__ = (
        PrimaryKeyConstraint("ClassID", "StudentID"),
        ForeignKeyConstraint(
            ["CourseID", "ClassID"],
            ["classes.CourseID", "classes.ClassID"]
        ),
        ForeignKeyConstraint(
            ["StudentID"],
            ["students.UserID"]
        ),
        # ── Indexes để tối ưu truy vấn ──────────────────────
        Index("idx_enrollment_student",       "StudentID"),
        Index("idx_enrollment_class",         "CourseID", "ClassID"),
        Index("idx_enrollment_status",        "Status"),
        Index("idx_enrollment_student_status","StudentID", "Status"),
        Index("idx_enrollment_class_score",   "CourseID", "ClassID", "FinalTermScore"),
    )

    # relationships
    class_   = relationship("Class",   back_populates="enrollments",
                             foreign_keys=[class_id, course_id])
    student  = relationship("Student", back_populates="enrollments",
                             foreign_keys=[student_id])


# ============================================================
# SECTION 6: ASSIGNMENT & REPORTS
# ============================================================

class Assignment(Base):
    """
    ERD: AssignmentID (PK), AssignmentName, Deadline, ClassID.
    Linked to Class (not directly to TeacherClass per ERD node).
    Also linked to TeacherClass for teacher assignment tracking.
    """
    __tablename__ = "assignments"

    assignment_id   = Column("AssignmentID",   String(10), primary_key=True)
    assignment_name = Column("AssignmentName", String(50), nullable=False)
    deadline        = Column("Deadline",       DateTime)
    class_id        = Column("ClassID",        String(10), nullable=False)
    course_id       = Column("CourseID",       String(10), nullable=False)
    teacher_id      = Column("TeacherID",      String(10))           # link to TeacherClass
    semester        = Column("Semester",       String(10))           # link to TeacherClass
    link_url        = Column("LinkURL",        String(500))          # Link đến bài tập

    __table_args__ = (
        ForeignKeyConstraint(
            ["CourseID", "ClassID"],
            ["classes.CourseID", "classes.ClassID"]
        ),
        ForeignKeyConstraint(
            ["TeacherID", "Semester", "ClassID"],
            ["teacher_classes.TeacherID", "teacher_classes.Semester", "teacher_classes.ClassID"]
        ),
        Index("idx_assignment_class", "CourseID", "ClassID"),
    )

    # relationships
    class_        = relationship("Class",        back_populates="assignments",
                                  foreign_keys=[course_id, class_id],
                                  overlaps="assignments,teacher_class")
    teacher_class = relationship("TeacherClass", back_populates="assignments",
                                  foreign_keys=[teacher_id, semester, class_id],
                                  overlaps="assignments,class_")
    reports       = relationship("AssignmentReport", back_populates="assignment")


class AssignmentReport(Base):
    """
    PK composite: (AssignmentID, StudentID) — bài nộp của sinh viên.
    """
    __tablename__ = "assignment_reports"

    assignment_id = Column("AssignmentID", String(10), ForeignKey("assignments.AssignmentID"), nullable=False)
    class_id      = Column("ClassID",      String(10), nullable=False)
    submit_date   = Column("SubmitDate",   DateTime)
    student_id    = Column("StudentID",    String(10), nullable=False)
    lesson_id     = Column("LessonID",     String(10))
    link_url      = Column("LinkURL",      String(500))
    grade         = Column("Grade",        Float)        # Điểm GV chấm (0-10)
    feedback      = Column("Feedback",     String(500))  # Nhận xét của GV

    __table_args__ = (
        PrimaryKeyConstraint("AssignmentID", "StudentID"),
        ForeignKeyConstraint(
            ["StudentID"],
            ["students.UserID"]
        ),
        Index("idx_assignment_report_student", "StudentID"),
        Index("idx_assignment_report_class",   "ClassID"),
    )

    # relationships
    assignment = relationship("Assignment", back_populates="reports")
    student    = relationship("Student",    back_populates="assignment_reports",
                               foreign_keys=[student_id])


class LessonReport(Base):
    """
    ERD: PK = (ClassID, Day, StudentID, LessonID).
    Điểm danh từng buổi học.
    """
    __tablename__ = "lesson_reports"

    class_id                 = Column("ClassID",               String(10), nullable=False)
    course_id                = Column("CourseID",              String(10), nullable=False)
    day                      = Column("Day",                   DateTime,   nullable=False)
    student_id               = Column("StudentID",             String(10), nullable=False)
    lesson_id                = Column("LessonID",              String(10), nullable=False)
    absent                   = Column("Absent",                Boolean,    nullable=False, default=False)
    submit_assignment_status = Column("SubmitAssignmentStatus", Boolean,   nullable=False, default=False)

    __table_args__ = (
        PrimaryKeyConstraint("ClassID", "Day", "StudentID", "LessonID"),
        ForeignKeyConstraint(
            ["CourseID", "ClassID"],
            ["classes.CourseID", "classes.ClassID"]
        ),
        ForeignKeyConstraint(
            ["StudentID"],
            ["students.UserID"]
        ),
        Index("idx_lesson_report_student", "StudentID"),
        Index("idx_lesson_report_class",   "CourseID", "ClassID"),
    )

    # relationships
    class_  = relationship("Class",   back_populates="lesson_reports",
                            foreign_keys=[course_id, class_id])
    student = relationship("Student", back_populates="lesson_reports",
                            foreign_keys=[student_id])


# ============================================================
# SECTION 7: DOCUMENTS
# ============================================================

class Document(Base):
    """ERD: DocumentID (PK), DocumentName, Deadline, TeacherID, CourseID, ClassID."""
    __tablename__ = "documents"

    document_id   = Column("DocumentID",   String(10), primary_key=True)
    document_name = Column("DocumentName", String(50), nullable=False)
    deadline      = Column("Deadline",     DateTime)
    teacher_id    = Column("TeacherID",    String(10), ForeignKey("teachers.TeacherID"))
    link_url      = Column("LinkURL",      String(500))
    course_id     = Column("CourseID",     String(10))  # Mã môn học
    class_id      = Column("ClassID",      String(10))  # Mã lớp học

    # relationships
    teacher = relationship("Teacher", back_populates="documents")


# ============================================================
# SECTION 8: LOGGING
# ============================================================

class ReportLog(Base):
    """
    ERD: LogID INT (PK, autoincrement), UserID, IP, Content VARCHAR(1000), TimeLog DATETIME.
    """
    __tablename__ = "report_logs"

    log_id   = Column("LogID",   Integer,     primary_key=True, autoincrement=True)
    user_id  = Column("UserID",  String(10),  ForeignKey("users.UserID"), nullable=False)
    ip       = Column("IP",      String(20))
    content  = Column("Content", String(1000))
    time_log = Column("TimeLog", DateTime,    nullable=False)

    # relationships
    user = relationship("User", back_populates="report_logs")


class SystemLog(Base):
    """
    ERD: LogID VARCHAR(10) (PK), IP, Action VARCHAR(10), UserID, Content VARCHAR(1000), TimeLog DATETIME.
    """
    __tablename__ = "system_logs"

    log_id   = Column("LogID",   String(10),  primary_key=True)
    ip       = Column("IP",      String(20))
    action   = Column("Action",  String(10))              # VARCHAR(10) per ERD
    user_id  = Column("UserID",  String(10),  ForeignKey("users.UserID"))
    content  = Column("Content", String(1000))
    time_log = Column("TimeLog", DateTime,    nullable=False)

    # relationships
    user = relationship("User", back_populates="system_logs")
