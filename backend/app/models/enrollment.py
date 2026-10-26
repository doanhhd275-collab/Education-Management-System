"""
models/enrollment.py — Enrollment (Đăng ký học tập)

PK = (ClassID, StudentID).
FK ClassID+CourseID → classes composite PK.
FK StudentID        → students.UserID.
"""
from sqlalchemy import (
    Column, String, Float,
    ForeignKeyConstraint, PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Enrollment(Base):
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
        Index("idx_enrollment_student",        "StudentID"),
        Index("idx_enrollment_class",          "CourseID", "ClassID"),
        Index("idx_enrollment_status",         "Status"),
        Index("idx_enrollment_student_status", "StudentID", "Status"),
        Index("idx_enrollment_class_score",    "CourseID", "ClassID", "FinalTermScore"),
    )

    # relationships
    class_  = relationship("Class",   back_populates="enrollments",
                           foreign_keys=[class_id, course_id])
    student = relationship("Student", back_populates="enrollments",
                           foreign_keys=[student_id])
