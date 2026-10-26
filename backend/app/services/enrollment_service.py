"""
services/enrollment_service.py — Business logic cho Enrollment (Đăng ký học tập)

Trách nhiệm:
  - Kiểm tra điều kiện đăng ký (lớp còn chỗ, sinh viên tồn tại, chưa đăng ký)
  - CRUD enrollment
  - Role-based filtering (student chỉ xem của mình)
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.class_ import Class
from app.models.student import Student


class EnrollmentService:

    @staticmethod
    def list_enrollments(
        db: Session,
        current_user,
        student_id: str | None = None,
        class_id: str | None = None,
        course_id: str | None = None,
        status_: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[Enrollment]:
        query = db.query(Enrollment)

        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids:
            query = query.filter(Enrollment.student_id == current_user.user_id)
        else:
            if student_id:
                query = query.filter(Enrollment.student_id == student_id)

        if class_id:
            query = query.filter(Enrollment.class_id == class_id)
        if course_id:
            query = query.filter(Enrollment.course_id == course_id)
        if status_:
            query = query.filter(Enrollment.status == status_)

        return query.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def enroll(db: Session, current_user, class_id: str, course_id: str, student_id: str) -> Enrollment:
        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "STUDENT" in role_ids and "ADMIN" not in role_ids:
            if student_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Bạn chỉ được đăng ký cho bản thân")

        class_ = db.query(Class).filter(
            Class.course_id == course_id, Class.class_id == class_id
        ).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

        if not db.query(Student).filter(Student.user_id == student_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

        if db.query(Enrollment).filter(
            Enrollment.class_id == class_id,
            Enrollment.student_id == student_id
        ).first():
            raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký lớp này rồi")

        if class_.capacity:
            current_count = db.query(Enrollment).filter(
                Enrollment.class_id == class_id,
                Enrollment.course_id == course_id
            ).count()
            if current_count >= class_.capacity:
                raise HTTPException(status_code=400, detail="Lớp học đã đầy")

        enrollment = Enrollment(
            class_id=class_id, course_id=course_id, student_id=student_id, status="STUDYING"
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def get_enrollment(db: Session, current_user, class_id: str, student_id: str) -> Enrollment:
        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "STUDENT" in role_ids and "ADMIN" not in role_ids and "TEACHER" not in role_ids:
            if current_user.user_id != student_id:
                raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")

        enrollment = db.query(Enrollment).filter(
            Enrollment.class_id == class_id,
            Enrollment.student_id == student_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")
        return enrollment

    @staticmethod
    def update_enrollment(db: Session, class_id: str, student_id: str, update_data: dict) -> Enrollment:
        enrollment = db.query(Enrollment).filter(
            Enrollment.class_id == class_id,
            Enrollment.student_id == student_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")
        for field, value in update_data.items():
            setattr(enrollment, field, value)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def cancel_enrollment(db: Session, class_id: str, student_id: str) -> None:
        enrollment = db.query(Enrollment).filter(
            Enrollment.class_id == class_id,
            Enrollment.student_id == student_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký")
        db.delete(enrollment)
        db.commit()
