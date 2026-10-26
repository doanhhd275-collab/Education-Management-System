"""
models/user.py — User, Role, UserRole

Phần cốt lõi của hệ thống xác thực và phân quyền.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    role_id   = Column("RoleID",   String(10), primary_key=True)
    role_name = Column("RoleName", String(30), nullable=False)

    # relationships
    user_roles = relationship("UserRole", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id  = Column("UserID",    String(10),  primary_key=True)
    email    = Column("Email",     String(50),  nullable=False, unique=True)
    password = Column("Password",  String(255), nullable=False)
    contact  = Column("Contact",   String(15))
    birth    = Column("BirthDate", DateTime)
    name     = Column("Name",      String(30),  nullable=False)

    # relationships
    user_roles  = relationship("UserRole",  back_populates="user")
    student     = relationship("Student",   back_populates="user", uselist=False)
    teacher     = relationship("Teacher",   back_populates="user", uselist=False)
    report_logs = relationship("ReportLog", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")


class UserRole(Base):
    """Junction table: User ↔ Role (Many-to-Many)."""
    __tablename__ = "user_roles"

    user_id = Column("UserID", String(10), ForeignKey("users.UserID"),  primary_key=True)
    role_id = Column("RoleID", String(10), ForeignKey("roles.RoleID"),  primary_key=True)

    # relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
