"""
Database Seeder — chạy tự động khi app khởi động.

Nguyên tắc:
  - Chỉ INSERT nếu record CHƯA tồn tại (idempotent — an toàn để chạy nhiều lần).
  - Không bao giờ ghi đè dữ liệu đã có.
  - Tạo đủ dữ liệu để hệ thống có thể dùng ngay sau deploy.
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import Role, User, UserRole, Student, Teacher, Curriculum, Course

logger = logging.getLogger(__name__)


# ── Dữ liệu mặc định ────────────────────────────────────────────────────────

DEFAULT_ROLES = [
    {"role_id": "ADMIN",   "role_name": "Quản trị viên"},
    {"role_id": "TEACHER", "role_name": "Giáo viên"},
    {"role_id": "STUDENT", "role_name": "Sinh viên"},
]

DEFAULT_USERS = [
    {
        "user_id":  "U001",
        "email":    "admin@ems.edu.vn",
        "password": "Admin@123",
        "name":     "Quản Trị Viên",
        "contact":  "0900000001",
        "roles":    ["ADMIN"],
    },
    {
        "user_id":  "U002",
        "email":    "teacher1@ems.edu.vn",
        "password": "Admin@123",
        "name":     "Nguyễn Văn Giảng",
        "contact":  "0900000002",
        "roles":    ["TEACHER"],
        "teacher_id": "T001",
    },
    {
        "user_id":  "U003",
        "email":    "teacher2@ems.edu.vn",
        "password": "Admin@123",
        "name":     "Trần Thị Bình",
        "contact":  "0900000003",
        "roles":    ["TEACHER"],
        "teacher_id": "T002",
    },
    {
        "user_id":  "U004",
        "email":    "student1@ems.edu.vn",
        "password": "Admin@123",
        "name":     "Lê Văn Học",
        "contact":  "0900000004",
        "roles":    ["STUDENT"],
        "student": True,
    },
    {
        "user_id":  "U005",
        "email":    "student2@ems.edu.vn",
        "password": "Admin@123",
        "name":     "Phạm Thị Sinh",
        "contact":  "0900000005",
        "roles":    ["STUDENT"],
        "student": True,
    },
]

DEFAULT_CURRICULUMS = [
    {"program_id": "CS2024",  "program_name": "Khoa học Máy tính"},
    {"program_id": "IT2024",  "program_name": "Công nghệ Thông tin"},
    {"program_id": "SE2024",  "program_name": "Kỹ thuật Phần mềm"},
]

DEFAULT_COURSES = [
    {"course_id": "CS101", "course_name": "Nhập môn Lập trình"},
    {"course_id": "CS201", "course_name": "Cấu trúc Dữ liệu & Giải thuật"},
    {"course_id": "CS301", "course_name": "Cơ sở Dữ liệu"},
    {"course_id": "CS401", "course_name": "Lập trình Web"},
    {"course_id": "CS501", "course_name": "Mạng Máy tính"},
]


# ── Hàm seed chính ──────────────────────────────────────────────────────────

def seed_database() -> None:
    """
    Entry point — được gọi từ startup event của FastAPI.
    Tạo session riêng, seed toàn bộ dữ liệu mặc định, rồi đóng session.
    """
    db: Session = SessionLocal()
    try:
        _seed_roles(db)
        _seed_users(db)
        _seed_curriculums(db)
        _seed_courses(db)
        db.commit()
        logger.info("✅ Seed database hoàn tất.")
    except Exception as exc:
        db.rollback()
        logger.error("❌ Seed database thất bại: %s", exc, exc_info=True)
    finally:
        db.close()


# ── Các hàm seed riêng lẻ ────────────────────────────────────────────────────

def _seed_roles(db: Session) -> None:
    """Tạo 3 roles: ADMIN, TEACHER, STUDENT — bỏ qua nếu đã tồn tại."""
    for r in DEFAULT_ROLES:
        if not db.get(Role, r["role_id"]):
            db.add(Role(role_id=r["role_id"], role_name=r["role_name"]))
            logger.info("  + Role: %s", r["role_id"])
    db.flush()


def _seed_users(db: Session) -> None:
    """Tạo users mặc định + gán role + tạo student/teacher profile."""
    for u in DEFAULT_USERS:
        # Bỏ qua nếu user đã tồn tại (kiểm tra qua email để an toàn hơn)
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            continue

        user = User(
            user_id=u["user_id"],
            email=u["email"],
            password=hash_password(u["password"]),
            name=u["name"],
            contact=u.get("contact"),
        )
        db.add(user)
        db.flush()  # flush để user_id tồn tại trong session trước khi gán role

        # Gán role(s)
        for role_id in u.get("roles", []):
            db.add(UserRole(user_id=u["user_id"], role_id=role_id))

        # Tạo Teacher profile
        if "teacher_id" in u:
            db.add(Teacher(teacher_id=u["teacher_id"], user_id=u["user_id"]))

        # Tạo Student profile (không gán chương trình — để trống)
        if u.get("student"):
            db.add(Student(user_id=u["user_id"]))

        logger.info("  + User: %s (%s)", u["email"], u["roles"])

    db.flush()


def _seed_curriculums(db: Session) -> None:
    """Tạo các chương trình đào tạo mặc định."""
    for c in DEFAULT_CURRICULUMS:
        if not db.get(Curriculum, c["program_id"]):
            db.add(Curriculum(program_id=c["program_id"], program_name=c["program_name"]))
            logger.info("  + Curriculum: %s", c["program_id"])
    db.flush()


def _seed_courses(db: Session) -> None:
    """Tạo các môn học mặc định."""
    for c in DEFAULT_COURSES:
        if not db.get(Course, c["course_id"]):
            db.add(Course(course_id=c["course_id"], course_name=c["course_name"]))
            logger.info("  + Course: %s", c["course_id"])
    db.flush()
