"""
services/user_service.py — Business logic cho User management

Trách nhiệm:
  - CRUD user (list, create, get, update, delete)
  - Gán / gỡ role cho user
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.user import User, UserRole, Role


def _load_user_with_roles(db: Session, user_id: str) -> User | None:
    """Helper: load User + user_roles (eager) để tránh lazy-load."""
    return (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .filter(User.user_id == user_id)
        .first()
    )


class UserService:

    @staticmethod
    def list_users(db: Session, page: int = 1, page_size: int = 50) -> list[User]:
        offset = (page - 1) * page_size
        return (
            db.query(User)
            .options(joinedload(User.user_roles).joinedload(UserRole.role))
            .offset(offset)
            .limit(page_size)
            .all()
        )

    @staticmethod
    def create_user(db: Session, user_id: str, email: str, password: str,
                    name: str, contact: str | None = None, birth=None) -> User:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{email}' đã được sử dụng",
            )
        if db.query(User).filter(User.user_id == user_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã người dùng '{user_id}' đã tồn tại",
            )

        new_user = User(
            user_id  = user_id,
            email    = email,
            password = hash_password(password),
            contact  = contact,
            birth    = birth,
            name     = name,
        )
        db.add(new_user)
        db.commit()
        return _load_user_with_roles(db, new_user.user_id)

    @staticmethod
    def get_user(db: Session, user_id: str) -> User:
        user = _load_user_with_roles(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, update_data: dict) -> User:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        return _load_user_with_roles(db, user_id)

    @staticmethod
    def delete_user(db: Session, user_id: str) -> None:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        db.delete(user)
        db.commit()

    @staticmethod
    def assign_role(db: Session, user_id: str, role_id: str) -> dict:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")

        role = db.query(Role).filter(Role.role_id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_id}' không tồn tại")

        if db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).first():
            raise HTTPException(status_code=400, detail="User đã có role này rồi")

        db.add(UserRole(user_id=user_id, role_id=role_id))
        db.commit()
        return {"message": f"Gán role '{role.role_name}' cho '{user.name}' thành công"}

    @staticmethod
    def remove_role(db: Session, user_id: str, role_id: str) -> None:
        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        if not user_role:
            raise HTTPException(status_code=404, detail="User không có role này")
        db.delete(user_role)
        db.commit()
