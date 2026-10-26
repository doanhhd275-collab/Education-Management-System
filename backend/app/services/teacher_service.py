"""
services/teacher_service.py — Business logic cho Teacher management
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.models.teacher import Teacher
from app.models.class_ import TeacherClass


class TeacherService:

    @staticmethod
    def list_teachers(db: Session, page: int = 1, page_size: int = 20) -> list[Teacher]:
        return (
            db.query(Teacher)
            .options(joinedload(Teacher.user))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    @staticmethod
    def create_teacher(db: Session, teacher_id: str, user_id: str) -> Teacher:
        if not db.query(User).filter(User.user_id == user_id).first():
            raise HTTPException(status_code=404, detail=f"Không tìm thấy user '{user_id}'")
        if db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
            raise HTTPException(status_code=400, detail=f"TeacherID '{teacher_id}' đã tồn tại")
        if db.query(Teacher).filter(Teacher.user_id == user_id).first():
            raise HTTPException(status_code=400, detail="User này đã là giáo viên")

        new_teacher = Teacher(teacher_id=teacher_id, user_id=user_id)
        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        return new_teacher

    @staticmethod
    def get_teacher(db: Session, teacher_id: str) -> Teacher:
        teacher = (
            db.query(Teacher)
            .options(joinedload(Teacher.user))
            .filter(Teacher.teacher_id == teacher_id)
            .first()
        )
        if not teacher:
            raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
        return teacher

    @staticmethod
    def get_my_info(db: Session, user_id: str) -> dict:
        """Lấy thông tin teacher của user đang đăng nhập."""
        teacher = (
            db.query(Teacher)
            .options(joinedload(Teacher.user))
            .filter(Teacher.user_id == user_id)
            .first()
        )
        if not teacher:
            raise HTTPException(status_code=404, detail="Bạn chưa được đăng ký là giáo viên trong hệ thống")
        return {
            "teacher_id": teacher.teacher_id,
            "user_id":    teacher.user_id,
            "name":       teacher.user.name if teacher.user else "",
        }

    @staticmethod
    def get_classes(db: Session, teacher_id: str, semester: str | None = None) -> list[dict]:
        if not db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

        query = db.query(TeacherClass).filter(TeacherClass.teacher_id == teacher_id)
        if semester:
            query = query.filter(TeacherClass.semester == semester)

        return [
            {"class_id": tc.class_id, "course_id": tc.course_id, "semester": tc.semester}
            for tc in query.all()
        ]
