"""
services/document_service.py — Business logic cho Document management
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.teacher import Teacher


def _get_teacher_by_user(db: Session, user_id: str) -> Teacher | None:
    return db.query(Teacher).filter(Teacher.user_id == user_id).first()


class DocumentService:

    @staticmethod
    def list_documents(db: Session, teacher_id: str | None = None,
                       course_id: str | None = None, class_id: str | None = None,
                       page: int = 1, page_size: int = 20) -> list[Document]:
        query = db.query(Document)
        if teacher_id:
            query = query.filter(Document.teacher_id == teacher_id)
        if course_id:
            query = query.filter(Document.course_id == course_id)
        if class_id:
            query = query.filter(Document.class_id == class_id)
        return query.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def create_document(db: Session, current_user,
                        document_id: str, document_name: str,
                        deadline=None, teacher_id: str | None = None,
                        link_url: str | None = None,
                        course_id: str | None = None,
                        class_id: str | None = None) -> Document:
        role_ids = [ur.role_id for ur in current_user.user_roles]

        if "TEACHER" not in role_ids and "ADMIN" not in role_ids:
            raise HTTPException(status_code=403, detail="Chỉ giáo viên hoặc admin mới được đăng tài liệu")

        # Teacher: dùng teacher_id của bản thân
        if "TEACHER" in role_ids and "ADMIN" not in role_ids:
            teacher = _get_teacher_by_user(db, current_user.user_id)
            if not teacher:
                raise HTTPException(status_code=400, detail="Tài khoản của bạn chưa được liên kết với hồ sơ giáo viên")
            teacher_id = teacher.teacher_id
        else:
            # Admin: dùng teacher_id từ request (optional)
            if teacher_id and not db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
                raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

        if db.query(Document).filter(Document.document_id == document_id).first():
            raise HTTPException(status_code=400, detail=f"DocumentID '{document_id}' đã tồn tại")

        doc = Document(
            document_id=document_id, document_name=document_name,
            deadline=deadline, teacher_id=teacher_id,
            link_url=link_url, course_id=course_id, class_id=class_id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_document(db: Session, document_id: str) -> Document:
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
        return doc

    @staticmethod
    def update_document(db: Session, current_user, document_id: str, update_data: dict) -> Document:
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "TEACHER" in role_ids and "ADMIN" not in role_ids:
            teacher = _get_teacher_by_user(db, current_user.user_id)
            if not teacher or doc.teacher_id != teacher.teacher_id:
                raise HTTPException(status_code=403, detail="Bạn chỉ được sửa tài liệu của mình")

        for field, value in update_data.items():
            setattr(doc, field, value)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def delete_document(db: Session, current_user, document_id: str) -> None:
        doc = db.query(Document).filter(Document.document_id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

        role_ids = [ur.role_id for ur in current_user.user_roles]
        if "TEACHER" in role_ids and "ADMIN" not in role_ids:
            teacher = _get_teacher_by_user(db, current_user.user_id)
            if not teacher or doc.teacher_id != teacher.teacher_id:
                raise HTTPException(status_code=403, detail="Bạn chỉ được xóa tài liệu của mình")

        db.delete(doc)
        db.commit()
