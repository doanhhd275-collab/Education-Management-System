"""
core/logging.py — Cấu hình logging toàn cục cho ứng dụng

Gọi setup_logging() một lần duy nhất từ main.py trước khi app khởi động.
Sau đó các module dùng: logger = logging.getLogger(__name__)
"""
import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Cấu hình root logger với formatter chuẩn.

    Args:
        level: Log level string ("DEBUG", "INFO", "WARNING", "ERROR").
               Nếu None, dùng INFO.
    """
    from app.core.config import settings

    log_level = getattr(logging, (level or ("DEBUG" if settings.DEBUG else "INFO")).upper(), logging.INFO)

    # Formatter chuẩn: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Tránh duplicate handlers khi reload (uvicorn --reload)
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

    # Giảm noise từ các thư viện bên ngoài
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("✅ Logging đã được cấu hình (level=%s)", logging.getLevelName(log_level))
