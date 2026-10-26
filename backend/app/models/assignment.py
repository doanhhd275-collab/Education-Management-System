"""
models/assignment.py — Assignment + AssignmentReport (bài tập & bài nộp)
"""
from sqlalchemy import (
    Column, String, Float, DateTime,
    ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Assignment(Base):
    """
    ERD: AssignmentID (PK), AssignmentName, Deadline, ClassID.
    Linked to Class; also linked to TeacherClass for teacher tracking.
    """
    __tablename__ = "assignments"

    assignment_id   = Column("AssignmentID",   String(10),  primary_key=True)
    assignment_name = Column("AssignmentName", String(50),  nullable=False)
    deadline        = Column("Deadline",       DateTime)
    class_id        = Column("ClassID",        String(10),  nullable=False)
    course_id       = Column("CourseID",       String(10),  nullable=False)
    teacher_id      = Column("TeacherID",      String(10))
    semester        = Column("Semester",       String(10))
    link_url        = Column("LinkURL",        String(500))

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

    assignment_id = Column("AssignmentID", String(10),  ForeignKey("assignments.AssignmentID"), nullable=False)
    class_id      = Column("ClassID",      String(10),  nullable=False)
    submit_date   = Column("SubmitDate",   DateTime)
    student_id    = Column("StudentID",    String(10),  nullable=False)
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
