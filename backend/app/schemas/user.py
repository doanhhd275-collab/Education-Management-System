"""
Schemas cho User, Role, UserRole, Student, Teacher.
Mỗi entity có 3 lớp: Base → Create → Response
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# ROLE
# ============================================================

class RoleBase(BaseModel):
    role_name: str = Field(..., max_length=30)


class RoleCreate(RoleBase):
    role_id: str = Field(..., max_length=10)


class RoleResponse(RoleBase):
    role_id: str

    model_config = {"from_attributes": True}


# ============================================================
# USER
# ============================================================

class UserBase(BaseModel):
    email:    EmailStr
    contact:  Optional[str]  = Field(None, max_length=15)
    birth:    Optional[date] = None
    name:     str            = Field(..., max_length=30)


class UserCreate(UserBase):
    user_id:  str = Field(..., max_length=10)
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Chỉ cho phép cập nhật các trường không nhạy cảm."""
    email:   Optional[EmailStr] = None
    contact: Optional[str]     = Field(None, max_length=15)
    birth:   Optional[date]    = None
    name:    Optional[str]     = Field(None, max_length=30)


class UserResponse(UserBase):
    user_id: str
    user_roles: list["UserRoleResponse"] = []

    model_config = {"from_attributes": True}


# ============================================================
# USER ROLE  (junction)
# ============================================================

class UserRoleCreate(BaseModel):
    user_id: str = Field(..., max_length=10)
    role_id: str = Field(..., max_length=10)


class UserRoleResponse(UserRoleCreate):
    role: Optional["RoleResponse"] = None

    model_config = {"from_attributes": True}


# ============================================================
# STUDENT
# ============================================================

class StudentBase(BaseModel):
    program_id:           Optional[str]   = Field(None, max_length=10)
    cpa:                  Optional[float] = None
    gpa:                  Optional[float] = None
    warning_level:        Optional[int]   = None
    graduation_condition: Optional[bool]  = None


class StudentCreate(StudentBase):
    user_id: str = Field(..., max_length=10)


class StudentUpdate(BaseModel):
    cpa:                  Optional[float] = None
    gpa:                  Optional[float] = None
    warning_level:        Optional[int]   = None
    graduation_condition: Optional[bool]  = None


class StudentResponse(StudentBase):
    user_id: str
    # Thông tin User đính kèm (eager load)
    user: Optional["UserResponse"] = None

    model_config = {"from_attributes": True}


# ============================================================
# TEACHER
# ============================================================

class TeacherBase(BaseModel):
    teacher_id: str = Field(..., max_length=10)
    user_id:    str = Field(..., max_length=10)


class TeacherCreate(TeacherBase):
    pass


class TeacherResponse(TeacherBase):
    user: Optional["UserResponse"] = None

    model_config = {"from_attributes": True}


# Resolve forward references
UserResponse.model_rebuild()
UserRoleResponse.model_rebuild()
StudentResponse.model_rebuild()
TeacherResponse.model_rebuild()