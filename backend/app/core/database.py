from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Nạp file .env
load_dotenv()

# Lấy đường dẫn kết nối
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Tạo Engine (Động cơ kết nối)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo Session (Phiên làm việc để truy vấn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Re-export Base từ models.base để main.py vẫn import được
from app.models.base import Base  # noqa: E402