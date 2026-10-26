"""
Router: Authentication
Endpoints:
  POST /api/v1/auth/login   — Đăng nhập, trả về JWT token
  POST /api/v1/auth/logout  — Đăng xuất (client tự xóa token)
  GET  /api/v1/auth/me      — Lấy thông tin user đang đăng nhập
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, DbDep, CurrentUserDep
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, LogoutResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DbDep):
    """Đăng nhập hệ thống — kiểm tra email + password, trả về JWT token."""
    return AuthService.login(db, data.email, data.password)


@router.post("/logout", response_model=LogoutResponse)
def logout():
    """Đăng xuất (stateless — frontend tự xóa token)."""
    return LogoutResponse(message="Đăng xuất thành công")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUserDep, db: DbDep):
    """Lấy thông tin user đang đăng nhập (dựa vào JWT token)."""
    return AuthService.get_me(db, current_user.user_id)
