"""
Module: user_management
Service layer — business logic cho User, Student, Teacher, Role.
"""
from sqlalchemy.orm import Session

from app.models.user import User, Student, Teacher, Role, UserRole
from app.schemas.user import UserCreate, UserUpdate, StudentUpdate


# ── User ────────────────────────────────────────────────────

def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, page: int = 1, page_size: int = 20) -> list[User]:
    offset = (page - 1) * page_size
    return db.query(User).offset(offset).limit(page_size).all()


def create_user(db: Session, data: UserCreate, hashed_password: str) -> User:
    user = User(
        user_id  = data.user_id,
        email    = data.email,
        password = hashed_password,
        contact  = data.contact,
        birth    = data.birth,
        name     = data.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ── Role ────────────────────────────────────────────────────

def assign_role(db: Session, user_id: str, role_id: str) -> UserRole:
    existing = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
        .first()
    )
    if existing:
        return existing
    ur = UserRole(user_id=user_id, role_id=role_id)
    db.add(ur)
    db.commit()
    db.refresh(ur)
    return ur


def get_user_roles(db: Session, user_id: str) -> list[str]:
    """Trả về danh sách role_name của user."""
    rows = (
        db.query(Role.role_name)
        .join(UserRole, UserRole.role_id == Role.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [r.role_name for r in rows]


# ── Student ──────────────────────────────────────────────────

def get_student(db: Session, user_id: str, program_id: str) -> Student | None:
    return (
        db.query(Student)
        .filter(Student.user_id == user_id, Student.program_id == program_id)
        .first()
    )


def list_students(
    db: Session, program_id: str | None = None,
    page: int = 1, page_size: int = 20
) -> list[Student]:
    q = db.query(Student)
    if program_id:
        q = q.filter(Student.program_id == program_id)
    return q.offset((page - 1) * page_size).limit(page_size).all()


def update_student(db: Session, student: Student, data: StudentUpdate) -> Student:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


# ── Teacher ──────────────────────────────────────────────────

def get_teacher(db: Session, teacher_id: str) -> Teacher | None:
    return db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()


def list_teachers(
    db: Session, page: int = 1, page_size: int = 20
) -> list[Teacher]:
    return (
        db.query(Teacher)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
