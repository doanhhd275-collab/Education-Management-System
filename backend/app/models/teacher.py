"""
models/teacher.py — Teacher profile + CourseTeacher junction

Teacher: mỗi User có thể là một giáo viên (TeacherID riêng).
CourseTeacher: junction table Course ↔ Teacher (Many-to-Many).
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column("TeacherID", String(10), primary_key=True)
    user_id    = Column("UserID",    String(10), ForeignKey("users.UserID"), unique=True)

    # relationships
    user            = relationship("User",          back_populates="teacher")
    course_teachers = relationship("CourseTeacher", back_populates="teacher")
    teacher_classes = relationship("TeacherClass",  back_populates="teacher")
    documents       = relationship("Document",      back_populates="teacher")


class CourseTeacher(Base):
    """Junction table: Course ↔ Teacher (Many-to-Many)."""
    __tablename__ = "course_teachers"

    course_id  = Column("CourseID",  String(10), ForeignKey("courses.CourseID"),   primary_key=True)
    teacher_id = Column("TeacherID", String(10), ForeignKey("teachers.TeacherID"), primary_key=True)

    # relationships
    course  = relationship("Course",  back_populates="course_teachers")
    teacher = relationship("Teacher", back_populates="course_teachers")
