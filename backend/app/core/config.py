"""
core/config.py — Centralized application settings

Dùng Pydantic Settings để tập trung tất cả config vào một nơi.
Ưu tiên: environment variable > .env file > default value.
"""
import secrets
import logging
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ems"

    # ── JWT ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str = ""                  # sẽ được override trong validator
    JWT_ALGORITHM: str  = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://education-management-system-pi.vercel.app",
    ]

    # ── App ──────────────────────────────────────────────────
    APP_TITLE: str   = "Hệ Thống Quản Lý Đào Tạo (EMS)"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool      = False

    def model_post_init(self, __context) -> None:
        """Tự generate JWT_SECRET_KEY nếu không được cấu hình."""
        if not self.JWT_SECRET_KEY:
            object.__setattr__(self, "JWT_SECRET_KEY", secrets.token_hex(32))
            logger.warning(
                "JWT_SECRET_KEY không được cấu hình! "
                "Đang dùng key ngẫu nhiên — token sẽ bị mất hiệu lực khi restart server."
            )


@lru_cache
def get_settings() -> Settings:
    """
    Trả về singleton Settings instance (cached).
    Dùng lru_cache để chỉ parse .env một lần duy nhất.
    """
    return Settings()


# Convenience: instance dùng toàn app
settings = get_settings()
