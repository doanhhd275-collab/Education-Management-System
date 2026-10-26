"""
models/course.py — Course + CoursePrerequisite (self-referencing)
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    course_id   = Column("CourseID",   String(10), primary_key=True)
    course_name = Column("CourseName", String(30), nullable=False)

    # relationships
    classes            = relationship("Class",            back_populates="course")
    curriculum_courses = relationship("CurriculumCourse", back_populates="course")
    course_teachers    = relationship("CourseTeacher",    back_populates="course")
    # self-referencing: môn này YÊU CẦU các môn tiên quyết
    prerequisites_of   = relationship(
        "CoursePrerequisite",
        foreign_keys="[CoursePrerequisite.course_id]",
        back_populates="course",
        lazy="select"
    )
    # self-referencing: môn này LÀ tiên quyết của các môn khác
    required_by        = relationship(
        "CoursePrerequisite",
        foreign_keys="[CoursePrerequisite.prerequisite_course_id]",
        back_populates="prerequisite_course"
    )

    @property
    def prerequisites(self):
        """Alias cho prerequisites_of – dùng để CourseResponse serialize đúng field name."""
        return self.prerequisites_of


class CoursePrerequisite(Base):
    """Self-referencing: một Course có thể có nhiều môn tiên quyết."""
    __tablename__ = "course_prerequisites"

    course_id              = Column("CourseID",             String(10), ForeignKey("courses.CourseID"), primary_key=True)
    prerequisite_course_id = Column("PrerequisiteCourseID", String(10), ForeignKey("courses.CourseID"), primary_key=True)

    # relationships
    course              = relationship("Course", foreign_keys=[course_id],              back_populates="prerequisites_of")
    prerequisite_course = relationship("Course", foreign_keys=[prerequisite_course_id], back_populates="required_by")

    @property
    def prerequisite_course_name(self) -> str | None:
        """Tên môn tiên quyết – dùng để serialize trong CoursePrerequisiteResponse."""
        return self.prerequisite_course.course_name if self.prerequisite_course else None
