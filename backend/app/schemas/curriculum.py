"""
Schemas cho Curriculum, Course, CurriculumCourse, CoursePrerequisite.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================
# CURRICULUM (Chương trình đào tạo)
# ============================================================

class CurriculumBase(BaseModel):
    program_name: str = Field(..., max_length=30)


class CurriculumCreate(CurriculumBase):
    program_id: str = Field(..., max_length=10)


class CurriculumUpdate(BaseModel):
    program_name: Optional[str] = Field(None, max_length=30)


class CurriculumResponse(CurriculumBase):
    program_id: str
    curriculum_courses: Optional[List["CurriculumCourseResponse"]] = None

    model_config = {"from_attributes": True}


# ============================================================
# COURSE (Môn học)
# ============================================================

class CourseBase(BaseModel):
    course_name: str = Field(..., max_length=30)


class CourseCreate(CourseBase):
    course_id: str = Field(..., max_length=10)


class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, max_length=30)


class CourseResponse(CourseBase):
    course_id: str

    model_config = {"from_attributes": True}


# ============================================================
# CURRICULUM COURSE  (junction: Curriculum ↔ Course)
# ============================================================

class CourseInfo(BaseModel):
    """Thông tin tối giản của môn học để nhúng vào CurriculumCourseResponse."""
    course_id:   str
    course_name: str

    model_config = {"from_attributes": True}


class CurriculumCourseCreate(BaseModel):
    program_id: str = Field(..., max_length=10)
    course_id:  str = Field(..., max_length=10)


class CurriculumCourseResponse(CurriculumCourseCreate):
    course: Optional[CourseInfo] = None

    model_config = {"from_attributes": True}


# ============================================================
# COURSE PREREQUISITE  (self-referencing)
# ============================================================

class CoursePrerequisiteCreate(BaseModel):
    course_id:              str = Field(..., max_length=10)
    prerequisite_course_id: str = Field(..., max_length=10)


class CoursePrerequisiteResponse(CoursePrerequisiteCreate):
    model_config = {"from_attributes": True}


# Resolve forward references (Pydantic v2)
CurriculumResponse.model_rebuild()
