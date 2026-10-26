"""
services/auth_service.py — Business logic cho Authentication

Trách nhiệm:
  - Xác thực email/password
  - Tạo JWT token
  - Lấy current user từ token
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import verify_password, create_access_token
from app.models.user import User, UserRole


class AuthService:

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """
        Xác thực đăng nhập và trả về token + metadata.

        Returns:
            dict với access_token, token_type, expires_in, user_id, roles
        Raises:
            HTTPException 401 nếu sai email/password
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng",
            )

        roles = [ur.role_id for ur in db.query(UserRole).filter(UserRole.user_id == user.user_id).all()]
        token = create_access_token(user_id=user.user_id, roles=roles)

        return {
            "access_token": token,
            "token_type":   "bearer",
            "expires_in":   86400,  # 24 giờ (giây)
        }

    @staticmethod
    def get_me(db: Session, user_id: str) -> User:
        """
        Lấy thông tin user hiện tại với eager-load roles.
        """
        user = (
            db.query(User)
            .options(joinedload(User.user_roles).joinedload(UserRole.role))
            .filter(User.user_id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy user")
        return user
