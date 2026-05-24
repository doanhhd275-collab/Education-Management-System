"""
Schemas cho Enrollment.
Index-heavy table → schema phản ánh đủ các trường để hỗ trợ filter.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# ENROLLMENT  (PK composite: ClassID + StudentID)
# ============================================================

class EnrollmentBase(BaseModel):
    class_id:         str            = Field(..., max_length=10)
    course_id:        str            = Field(..., max_length=10)
    student_id:       str            = Field(..., max_length=10)


class EnrollmentCreate(EnrollmentBase):
    """Dữ liệu tối thiểu để đăng ký lớp (điểm chưa có)."""
    pass


class EnrollmentUpdate(BaseModel):
    """Giáo viên / Admin nhập điểm và cập nhật trạng thái."""
    midterm_score:    Optional[float] = Field(None, ge=0, le=10)
    final_term_score: Optional[float] = Field(None, ge=0, le=10)
    grade:            Optional[str]   = Field(None, max_length=1,
                                              description="Xếp loại: A, B, C, D, F")
    status:           Optional[str]   = Field(None, max_length=10,
                                              description="STUDYING | PASSED | FAILED")


class EnrollmentResponse(EnrollmentBase):
    midterm_score:    Optional[float] = None
    final_term_score: Optional[float] = None
    grade:            Optional[str]   = None
    status:           Optional[str]   = None

    model_config = {"from_attributes": True}


class EnrollmentListFilter(BaseModel):
    """Query params cho endpoint GET /enrollments (filter + pagination)."""
    student_id: Optional[str] = None
    class_id:   Optional[str] = None
    course_id:  Optional[str] = None
    status:     Optional[str] = None
    page:       int           = Field(1,   ge=1)
    page_size:  int           = Field(20,  ge=1, le=100)
