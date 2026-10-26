"""
models/student.py — Student profile (extends User)

Mỗi User chỉ là sinh viên của 1 chương trình (đơn giản cho project học thuật).
PK = UserID (single) để Enrollment có thể FK vào students.UserID.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Student(Base):
    __tablename__ = "students"

    user_id              = Column("UserID",              String(10), ForeignKey("users.UserID"),         primary_key=True)
    program_id           = Column("ProgramID",           String(10), ForeignKey("curriculums.ProgramID"), nullable=True)
    cpa                  = Column("CPA",                 Float)
    gpa                  = Column("GPA",                 Float)
    warning_level        = Column("WarningLevel",        Integer, default=0)
    graduation_condition = Column("GraduationCondition", Boolean, default=False)

    # relationships
    user               = relationship("User",             back_populates="student")
    program            = relationship("Curriculum",       back_populates="students")
    enrollments        = relationship("Enrollment",       back_populates="student",
                                     foreign_keys="[Enrollment.student_id]")
    assignment_reports = relationship("AssignmentReport", back_populates="student",
                                     foreign_keys="[AssignmentReport.student_id]")
    lesson_reports     = relationship("LessonReport",    back_populates="student",
                                     foreign_keys="[LessonReport.student_id]")
