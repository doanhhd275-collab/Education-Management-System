"""
Schemas cho Class, CourseTeacher, TeacherClass.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# CLASS  (PK composite: CourseID + ClassID)
# ============================================================

class ClassBase(BaseModel):
    semester:     Optional[str] = Field(None, max_length=10)
    capacity:     Optional[int] = None
    day_of_week:  Optional[str] = Field(None, max_length=5, description="Thứ học: '2'-'7'")
    start_period: Optional[int] = Field(None, ge=1, le=12, description="Tiết bắt đầu (1-12)")
    end_period:   Optional[int] = Field(None, ge=1, le=12, description="Tiết kết thúc (1-12)")


class ClassCreate(ClassBase):
    course_id: str = Field(..., max_length=10)
    class_id:  str = Field(..., max_length=10)


class ClassUpdate(BaseModel):
    semester:     Optional[str] = Field(None, max_length=10)
    capacity:     Optional[int] = None
    day_of_week:  Optional[str] = Field(None, max_length=5)
    start_period: Optional[int] = Field(None, ge=1, le=12)
    end_period:   Optional[int] = Field(None, ge=1, le=12)


class ClassResponse(ClassBase):
    course_id:    str
    class_id:     str
    day_of_week:  Optional[str] = None
    start_period: Optional[int] = None
    end_period:   Optional[int] = None

    model_config = {"from_attributes": True}


# ============================================================
# COURSE TEACHER  (junction: Course ↔ Teacher)
# ============================================================

class CourseTeacherCreate(BaseModel):
    course_id:  str = Field(..., max_length=10)
    teacher_id: str = Field(..., max_length=10)


class CourseTeacherResponse(CourseTeacherCreate):
    model_config = {"from_attributes": True}


# ============================================================
# TEACHER CLASS  (PK composite: TeacherID + Semester + ClassID)
# ============================================================

class TeacherClassBase(BaseModel):
    teacher_id: str = Field(..., max_length=10)
    semester:   str = Field(..., max_length=10)
    class_id:   str = Field(..., max_length=10)
    course_id:  str = Field(..., max_length=10)


class TeacherClassCreate(TeacherClassBase):
    pass


class TeacherClassResponse(TeacherClassBase):
    model_config = {"from_attributes": True}
