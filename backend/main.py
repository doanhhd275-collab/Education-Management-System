"""
Entry point của FastAPI application.
Đăng ký tất cả routers và cấu hình middleware.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình logging trước tiên
from app.core.logging import setup_logging
setup_logging()

# Config tập trung
from app.core.config import settings

# Import tất cả models (để SQLAlchemy nhận diện, tạo bảng đúng thứ tự)
import app.models  # noqa: F401

# Import database engine và Base
from app.core.database import engine, Base

# Import seeder
from app.core.seed import seed_database

# Import tất cả routers
from app.api.v1 import (
    auth,
    users,
    students,
    teachers,
    curriculum,
    courses,
    classes,
    enrollments,
    documents,
    assignments,
    attendance,
    logs,
)


def _run_migrations():
    """
    Chạy các ALTER TABLE migration thủ công.
    Dùng IF NOT EXISTS — an toàn để chạy lại nhiều lần khi deploy.
    """
    import logging
    from sqlalchemy import text
    logger = logging.getLogger(__name__)
    migrations = [
        'ALTER TABLE documents ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);',
        'ALTER TABLE assignments ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);',
        'ALTER TABLE assignment_reports ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);',
        'ALTER TABLE classes ADD COLUMN IF NOT EXISTS "DayOfWeek" VARCHAR(5);',
        'ALTER TABLE classes ADD COLUMN IF NOT EXISTS "StartPeriod" INTEGER;',
        'ALTER TABLE classes ADD COLUMN IF NOT EXISTS "EndPeriod" INTEGER;',
        'ALTER TABLE classes ADD COLUMN IF NOT EXISTS "Room" VARCHAR(20);',
        'ALTER TABLE documents ADD COLUMN IF NOT EXISTS "CourseID" VARCHAR(10);',
        'ALTER TABLE documents ADD COLUMN IF NOT EXISTS "ClassID" VARCHAR(10);',
        'ALTER TABLE assignment_reports ADD COLUMN IF NOT EXISTS "Grade" FLOAT;',
        'ALTER TABLE assignment_reports ADD COLUMN IF NOT EXISTS "Feedback" VARCHAR(500);',
    ]
    try:
        with engine.connect() as conn:
            for sql in migrations:
                conn.execute(text(sql))
            conn.commit()
        logger.info("✅ Migration hoàn tất.")
    except Exception as e:
        logger.warning("⚠️ Migration warning (có thể bỏ qua nếu đã tồn tại): %s", e)


# ── Startup / Shutdown lifecycle ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Chạy khi app khởi động: tạo bảng DB + migration + seed dữ liệu mặc định."""
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    seed_database()
    yield


# ── Khởi tạo ứng dụng FastAPI ────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    description="""
    API cho hệ thống quản lý đào tạo với các module:
    - Quản lý người dùng (Admin, Giáo viên, Sinh viên)
    - Quản lý chương trình đào tạo & môn học
    - Quản lý lớp học
    - Đăng ký học tập
    - Quản lý tài nguyên (tài liệu, bài tập)
    - Quản lý hệ thống (logs)
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Đăng ký tất cả routers với prefix /api/v1 ────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=API_PREFIX)
app.include_router(users.router,       prefix=API_PREFIX)
app.include_router(students.router,    prefix=API_PREFIX)
app.include_router(teachers.router,    prefix=API_PREFIX)
app.include_router(curriculum.router,  prefix=API_PREFIX)
app.include_router(courses.router,     prefix=API_PREFIX)
app.include_router(classes.router,     prefix=API_PREFIX)
app.include_router(enrollments.router, prefix=API_PREFIX)
app.include_router(documents.router,   prefix=API_PREFIX)
app.include_router(assignments.router, prefix=API_PREFIX)
app.include_router(attendance.router,  prefix=API_PREFIX)
app.include_router(logs.router,        prefix=API_PREFIX)


# ── Health Check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra server đang chạy."""
    return {"status": "ok", "message": "EMS Backend đang chạy bình thường!"}


@app.get("/", tags=["Health"])
def root():
    """Root endpoint."""
    return {
        "message": "Hệ Thống Quản Lý Đào Tạo API",
        "docs":    "/docs",
        "redoc":   "/redoc",
    }