"""
models/document.py — Document (Tài liệu học tập)

ERD: DocumentID (PK), DocumentName, Deadline, TeacherID, CourseID, ClassID.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"

    document_id   = Column("DocumentID",   String(10),  primary_key=True)
    document_name = Column("DocumentName", String(50),  nullable=False)
    deadline      = Column("Deadline",     DateTime)
    teacher_id    = Column("TeacherID",    String(10),  ForeignKey("teachers.TeacherID"))
    link_url      = Column("LinkURL",      String(500))
    course_id     = Column("CourseID",     String(10))
    class_id      = Column("ClassID",      String(10))

    # relationships
    teacher = relationship("Teacher", back_populates="documents")
