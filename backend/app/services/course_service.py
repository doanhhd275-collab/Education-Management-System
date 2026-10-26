"""
services/course_service.py — Business logic cho Course management
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.course import Course, CoursePrerequisite


class CourseService:

    @staticmethod
    def list_courses(db: Session) -> list[Course]:
        return db.query(Course).all()

    @staticmethod
    def create_course(db: Session, course_id: str, course_name: str) -> Course:
        if db.query(Course).filter(Course.course_id == course_id).first():
            raise HTTPException(status_code=400, detail=f"CourseID '{course_id}' đã tồn tại")
        course = Course(course_id=course_id, course_name=course_name)
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def get_course(db: Session, course_id: str) -> Course:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        return course

    @staticmethod
    def update_course(db: Session, course_id: str, course_name: str | None = None) -> Course:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        if course_name:
            course.course_name = course_name
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete_course(db: Session, course_id: str) -> None:
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        db.delete(course)
        db.commit()

    @staticmethod
    def add_prerequisite(db: Session, course_id: str, prerequisite_course_id: str) -> CoursePrerequisite:
        if not db.query(Course).filter(Course.course_id == course_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        if not db.query(Course).filter(Course.course_id == prerequisite_course_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy môn tiên quyết")
        if course_id == prerequisite_course_id:
            raise HTTPException(status_code=400, detail="Môn học không thể là tiên quyết của chính nó")
        if db.query(CoursePrerequisite).filter(
            CoursePrerequisite.course_id == course_id,
            CoursePrerequisite.prerequisite_course_id == prerequisite_course_id
        ).first():
            raise HTTPException(status_code=400, detail="Môn tiên quyết này đã được thêm rồi")

        prereq = CoursePrerequisite(course_id=course_id, prerequisite_course_id=prerequisite_course_id)
        db.add(prereq)
        db.commit()
        db.refresh(prereq)
        return prereq

    @staticmethod
    def remove_prerequisite(db: Session, course_id: str, prereq_id: str) -> None:
        prereq = db.query(CoursePrerequisite).filter(
            CoursePrerequisite.course_id == course_id,
            CoursePrerequisite.prerequisite_course_id == prereq_id
        ).first()
        if not prereq:
            raise HTTPException(status_code=404, detail="Không tìm thấy môn tiên quyết này")
        db.delete(prereq)
        db.commit()
