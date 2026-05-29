"""
Schemas cho Assignment, AssignmentReport, LessonReport, Document.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# ASSIGNMENT
# ============================================================

class AssignmentBase(BaseModel):
    assignment_name: str           = Field(..., max_length=50)
    deadline:        Optional[datetime] = None
    class_id:        str           = Field(..., max_length=10)
    course_id:       str           = Field(..., max_length=10)


class AssignmentCreate(AssignmentBase):
    assignment_id: str           = Field(..., max_length=10)
    teacher_id:    Optional[str] = Field(None, max_length=10)
    semester:      Optional[str] = Field(None, max_length=10)
    link_url:      Optional[str] = Field(None, max_length=500, description="Link đến bài tập")


class AssignmentUpdate(BaseModel):
    assignment_name: Optional[str]      = Field(None, max_length=50)
    deadline:        Optional[datetime] = None
    link_url:        Optional[str]      = Field(None, max_length=500)


class AssignmentResponse(AssignmentBase):
    assignment_id: str
    teacher_id:    Optional[str] = None
    semester:      Optional[str] = None
    link_url:      Optional[str] = None

    model_config = {"from_attributes": True}


# ============================================================
# ASSIGNMENT REPORT  (PK: AssignmentID + StudentID)
# ============================================================

class AssignmentReportBase(BaseModel):
    assignment_id: str           = Field(..., max_length=10)
    student_id:    str           = Field(..., max_length=10)
    class_id:      str           = Field(..., max_length=10)
    lesson_id:     Optional[str] = Field(None, max_length=10)


class AssignmentReportCreate(AssignmentReportBase):
    submit_date: Optional[datetime] = None
    link_url:    Optional[str]      = Field(None, max_length=500, description="Link bài nộp")


class AssignmentReportResponse(AssignmentReportBase):
    submit_date:  Optional[datetime] = None
    link_url:     Optional[str]      = None
    student_name: Optional[str]      = None  # join từ User
    grade:        Optional[float]    = None  # Điểm GV chấm
    feedback:     Optional[str]      = None  # Nhận xét GV

    model_config = {"from_attributes": True}


class GradeSubmission(BaseModel):
    """Schema để giáo viên chấm điểm bài nộp."""
    grade:    float = Field(..., ge=0, le=10, description="Điểm từ 0 đến 10")
    feedback: Optional[str] = Field(None, max_length=500, description="Nhận xét")


# ============================================================
# LESSON REPORT  (PK: ClassID + Day + StudentID + LessonID)
# Điểm danh từng buổi học
# ============================================================

class LessonReportBase(BaseModel):
    class_id:   str      = Field(..., max_length=10)
    course_id:  str      = Field(..., max_length=10)
    day:        datetime
    student_id: str      = Field(..., max_length=10)
    lesson_id:  str      = Field(..., max_length=10)


class LessonReportCreate(LessonReportBase):
    absent:                   bool = False
    submit_assignment_status: bool = False


class LessonReportUpdate(BaseModel):
    """Giáo viên cập nhật điểm danh / trạng thái nộp bài."""
    absent:                   Optional[bool] = None
    submit_assignment_status: Optional[bool] = None


class LessonReportResponse(LessonReportBase):
    absent:                   bool = False
    submit_assignment_status: bool = False

    model_config = {"from_attributes": True}


# ============================================================
# DOCUMENT  (Tài liệu học tập)
# ============================================================

class DocumentBase(BaseModel):
    document_name: str                = Field(..., max_length=50)
    deadline:      Optional[datetime] = None
    teacher_id:    Optional[str]      = Field(None, max_length=10)  # auto-filled by backend
    link_url:      Optional[str]      = Field(None, max_length=500, description="Link đến tài liệu")
    course_id:     Optional[str]      = Field(None, max_length=10, description="Mã môn học")
    class_id:      Optional[str]      = Field(None, max_length=10, description="Mã lớp học")


class DocumentCreate(DocumentBase):
    document_id: str = Field(..., max_length=10)


class DocumentUpdate(BaseModel):
    document_name: Optional[str]      = Field(None, max_length=50)
    deadline:      Optional[datetime] = None
    link_url:      Optional[str]      = Field(None, max_length=500)
    course_id:     Optional[str]      = Field(None, max_length=10)
    class_id:      Optional[str]      = Field(None, max_length=10)


class DocumentResponse(DocumentBase):
    document_id: str
    teacher_id:  Optional[str] = None
    course_id:   Optional[str] = None
    class_id:    Optional[str] = None

    model_config = {"from_attributes": True}
