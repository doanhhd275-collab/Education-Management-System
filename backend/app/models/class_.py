"""
models/class_.py — Class + TeacherClass

Class: lớp học (composite PK: CourseID + ClassID).
TeacherClass: giáo viên dạy lớp trong một học kỳ cụ thể.
"""
from sqlalchemy import (
    Column, String, Integer,
    ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Class(Base):
    """
    ERD: PK = (CourseID, ClassID) – composite primary key.
    Capacity thay cho NumberOfStudent.
    """
    __tablename__ = "classes"

    course_id    = Column("CourseID",    String(10), ForeignKey("courses.CourseID"), nullable=False)
    class_id     = Column("ClassID",     String(10), nullable=False)
    semester     = Column("Semester",    String(10))
    capacity     = Column("Capacity",    Integer)
    day_of_week  = Column("DayOfWeek",   String(5))     # "2".."7" (Thứ 2-7)
    start_period = Column("StartPeriod", Integer)        # 1-12
    end_period   = Column("EndPeriod",   Integer)        # 1-12
    room         = Column("Room",        String(20))

    __table_args__ = (
        PrimaryKeyConstraint("CourseID", "ClassID"),
    )

    # relationships
    course          = relationship("Course",       back_populates="classes")
    teacher_classes = relationship("TeacherClass", back_populates="class_")
    enrollments     = relationship("Enrollment",   back_populates="class_")
    assignments     = relationship("Assignment",   back_populates="class_")
    lesson_reports  = relationship("LessonReport", back_populates="class_")


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
    teacher     = relationship("Teacher",    back_populates="teacher_classes")
    class_      = relationship("Class",      back_populates="teacher_classes")
    assignments = relationship("Assignment", back_populates="teacher_class",
                               overlaps="assignments,class_")
