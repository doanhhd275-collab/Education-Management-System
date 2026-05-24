"""
FastAPI dependencies dùng chung toàn bộ ứng dụng:
  - get_db         → trả về SQLAlchemy Session
  - get_current_user → lấy User từ JWT Bearer token
  - require_role   → kiểm tra role, dùng làm Dependency
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User

# Scheme này đọc token từ header: "Authorization: Bearer <token>"
# tokenUrl: địa chỉ endpoint để lấy token (dùng cho Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Database Session ─────────────────────────────────────────

def get_db():
    """
    Tạo một database session cho mỗi request.
    Tự động đóng khi request kết thúc (dù thành công hay lỗi).
    """
    db = SessionLocal()
    try:
        yield db      # "trả" session cho route handler
    finally:
        db.close()    # luôn đóng sau khi dùng xong


# ── Current User ─────────────────────────────────────────────

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Giải mã JWT token và trả về User tương ứng từ database.

    Cách dùng trong route:
        @router.get("/profile")
        def profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    # Lỗi 401 chuẩn khi token không hợp lệ
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Giải mã token → lấy payload
        payload = decode_token(token)
        user_id: str = payload.get("sub")   # "sub" = subject = user_id
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Tìm user trong database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise credentials_exception

    return user


# ── Role-Based Access Control (RBAC) ─────────────────────────

def require_role(*allowed_roles: str):
    """
    Dependency factory: kiểm tra user có role trong danh sách cho phép không.

    Cách dùng:
        # Chỉ ADMIN được vào
        @router.delete("/users/{id}", dependencies=[Depends(require_role("ADMIN"))])

        # ADMIN hoặc TEACHER đều được vào
        @router.get("/students", dependencies=[Depends(require_role("ADMIN", "TEACHER"))])
    """
    def _check_role(token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = decode_token(token)
            user_roles: list[str] = payload.get("roles", [])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ",
            )

        # Kiểm tra có ít nhất một role khớp
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cần có quyền: {' hoặc '.join(allowed_roles)}",
            )

    return _check_role


# ── Type Aliases (viết tắt tiện dùng trong router) ───────────
DbDep          = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User,    Depends(get_current_user)]
