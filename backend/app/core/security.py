"""
core/security.py — Security utilities

- Băm mật khẩu bằng bcrypt (dùng trực tiếp, không qua passlib)
- Tạo và giải mã JWT token (HS256, hết hạn sau ACCESS_TOKEN_EXPIRE_HOURS)

Config được lấy từ core/config.py thay vì đọc os.getenv trực tiếp.
"""
import bcrypt
import logging
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# Shorthand từ settings
SECRET_KEY                = settings.JWT_SECRET_KEY
ALGORITHM                 = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_HOURS = settings.ACCESS_TOKEN_EXPIRE_HOURS


# ── Băm mật khẩu (bcrypt trực tiếp) ────────────────────────

def hash_password(plain_password: str) -> str:
    """Băm mật khẩu plain-text → bcrypt hash để lưu vào DB."""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh plain-text với hash đã lưu trong DB. Trả về True nếu khớp."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ── JWT ─────────────────────────────────────────────────────

def create_access_token(user_id: str, roles: list[str]) -> str:
    """
    Tạo JWT access token chứa thông tin user.

    Args:
        user_id: ID của user (làm subject của token)
        roles:   Danh sách role, ví dụ ["ADMIN"] hoặc ["STUDENT"]

    Returns:
        JWT string đã được ký bằng SECRET_KEY
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub":   user_id,
        "roles": roles,
        "exp":   expire,
        "iat":   datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Giải mã và xác thực JWT token.

    Returns:
        dict payload chứa sub, roles, exp, iat

    Raises:
        JWTError: nếu token không hợp lệ hoặc đã hết hạn
    """
    # algorithms=[ALGORITHM] để chặn tấn công "alg: none"
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
