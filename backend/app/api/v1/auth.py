"""
Router: Authentication
Endpoints:
  POST /api/v1/auth/login   — Đăng nhập, trả về JWT token
  POST /api/v1/auth/logout  — Đăng xuất (client tự xóa token)
  GET  /api/v1/auth/me      — Lấy thông tin user đang đăng nhập
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_db, get_current_user
from app.models.user import User, UserRole, Role
from app.schemas.auth import LoginRequest, TokenResponse, LogoutResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống.
    - Kiểm tra email + password
    - Trả về JWT token kèm thông tin role
    """
    # 1. Tìm user theo email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    # 2. Kiểm tra mật khẩu
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    # 3. Lấy danh sách role_id của user (ADMIN / TEACHER / STUDENT)
    role_ids = (
        db.query(UserRole.role_id)
        .filter(UserRole.user_id == user.user_id)
        .all()
    )
    roles = [r.role_id for r in role_ids]  # ["ADMIN"] chứ không phải ["Quản trị viên"]

    # 4. Tạo JWT token
    token = create_access_token(user_id=user.user_id, roles=roles)


    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=86400  # 24 giờ (giây)
    )


@router.post("/logout", response_model=LogoutResponse)
def logout():
    """
    Đăng xuất.
    JWT là stateless nên backend không cần làm gì thêm.
    Frontend sẽ xóa token khỏi localStorage.
    """
    return LogoutResponse(message="Đăng xuất thành công")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Lấy thông tin user đang đăng nhập (dựa vào JWT token).
    Trả về thông tin đầy đủ gồm user_roles (có nested role).
    """
    from sqlalchemy.orm import joinedload

    # Eager load user_roles và role bên trong để tránh lazy load issue
    user = (
        db.query(User)
        .options(
            joinedload(User.user_roles).joinedload(UserRole.role)
        )
        .filter(User.user_id == current_user.user_id)
        .first()
    )
    return user

