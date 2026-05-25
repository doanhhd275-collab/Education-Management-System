"""
Entry point của FastAPI application.
Đăng ký tất cả routers và cấu hình middleware.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import models để SQLAlchemy nhận diện và tạo bảng
from app.models import user  # noqa: F401

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
    logger = logging.getLogger(__name__)
    try:
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text(
                'ALTER TABLE documents ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);'
            ))
            conn.execute(__import__('sqlalchemy').text(
                'ALTER TABLE assignments ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);'
            ))
            conn.execute(__import__('sqlalchemy').text(
                'ALTER TABLE assignment_reports ADD COLUMN IF NOT EXISTS "LinkURL" VARCHAR(500);'
            ))
            conn.commit()
        logger.info("✅ Migration hoàn tất.")
    except Exception as e:
        logger.warning("⚠️ Migration warning (có thể bỏ qua nếu đã tồn tại): %s", e)


# ── Startup / Shutdown lifecycle ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Chạy khi app khởi động: tạo bảng DB + migration + seed dữ liệu mặc định."""
    # 1. Tạo tất cả bảng nếu chưa có
    Base.metadata.create_all(bind=engine)
    # 2. Chạy migrations (thêm cột mới vào bảng đã tồn tại)
    _run_migrations()
    # 3. Seed dữ liệu mặc định (idempotent — an toàn chạy nhiều lần)
    seed_database()
    yield
    # (Cleanup nếu cần khi shutdown)


# ── Khởi tạo ứng dụng FastAPI ────────────────────────────────
app = FastAPI(
    title="Hệ Thống Quản Lý Đào Tạo (EMS)",
    description="""
    API cho hệ thống quản lý đào tạo với các module:
    - Quản lý người dùng (Admin, Giáo viên, Sinh viên)
    - Quản lý chương trình đào tạo & môn học
    - Quản lý lớp học
    - Đăng ký học tập
    - Quản lý tài nguyên (tài liệu, bài tập)
    - Quản lý hệ thống (logs)
    """,
    version="1.0.0",
    docs_url="/docs",       # Swagger UI tại /docs
    redoc_url="/redoc",     # ReDoc tại /redoc
    redirect_slashes=False,   # Tắt redirect /users → /users/ (tránh mất Authorization header)
    lifespan=lifespan,        # Đăng ký startup/shutdown lifecycle
)

# ── CORS Middleware (Gắn vào app ngay sau khi khởi tạo) ───────
app.add_middleware(
    CORSMiddleware,
    # Tạm thời mở rào cho tất cả (*) để test Vercel dễ dàng
    allow_origins=[
        "http://localhost:5173", # Để dành cho bạn test local
        "http://localhost:3000",
        "https://education-management-system-pi.vercel.app" # <--- TÊN MIỀN VERCEL CỦA BẠN (Tuyệt đối KHÔNG có dấu / ở cuối)
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# (create_all đã được gọi trong lifespan startup ở trên)

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
    return {
        "status": "ok",
        "message": "EMS Backend đang chạy bình thường!"
    }


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - chuyển hướng đến docs."""
    return {
        "message": "Hệ Thống Quản Lý Đào Tạo API",
        "docs": "/docs",
        "redoc": "/redoc"
    }