"""
models/curriculum.py — Curriculum (Chương trình đào tạo) + CurriculumCourse junction
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Curriculum(Base):
    """Chương trình đào tạo – tên bảng theo ERD: Curriculum."""
    __tablename__ = "curriculums"

    program_id   = Column("ProgramID",   String(10), primary_key=True)
    program_name = Column("ProgramName", String(30), nullable=False)

    # relationships
    students           = relationship("Student",          back_populates="program")
    curriculum_courses = relationship("CurriculumCourse", back_populates="curriculum")


class CurriculumCourse(Base):
    """Junction table: Curriculum ↔ Course (Many-to-Many)."""
    __tablename__ = "curriculum_courses"

    program_id = Column("ProgramID", String(10), ForeignKey("curriculums.ProgramID"), primary_key=True)
    course_id  = Column("CourseID",  String(10), ForeignKey("courses.CourseID"),      primary_key=True)

    # relationships
    curriculum = relationship("Curriculum", back_populates="curriculum_courses")
    course     = relationship("Course",     back_populates="curriculum_courses")
