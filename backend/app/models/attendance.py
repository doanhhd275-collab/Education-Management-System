"""
models/attendance.py — LessonReport (Điểm danh từng buổi học)

ERD: PK = (ClassID, Day, StudentID, LessonID).
"""
from sqlalchemy import (
    Column, String, Boolean, DateTime,
    ForeignKeyConstraint, PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class LessonReport(Base):
    """Điểm danh từng buổi học của sinh viên."""
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
