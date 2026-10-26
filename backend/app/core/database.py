"""
core/database.py — SQLAlchemy engine & session factory

Dùng settings từ core/config.py thay vì đọc os.getenv trực tiếp.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base  # noqa: F401 — re-export để main.py vẫn import được

# Tạo Engine (Động cơ kết nối)
engine = create_engine(settings.DATABASE_URL)

# Tạo Session factory (Phiên làm việc để truy vấn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)