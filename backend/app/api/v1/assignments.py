"""
Router: Quản lý bài tập (Assignments) + bài nộp (AssignmentReports)
Endpoints:
  GET    /api/v1/assignments                             — Danh sách bài tập
  POST   /api/v1/assignments                             — TEACHER: tạo bài tập
  GET    /api/v1/assignments/my-submissions              — STUDENT: bài nộp của mình
  GET    /api/v1/assignments/{assignment_id}             — Chi tiết bài tập
  PUT    /api/v1/assignments/{assignment_id}             — TEACHER: cập nhật
  DELETE /api/v1/assignments/{assignment_id}             — TEACHER/ADMIN: xóa
  GET    /api/v1/assignments/{assignment_id}/reports     — TEACHER: xem bài nộp
  POST   /api/v1/assignments/{assignment_id}/submit      — STUDENT: nộp bài
  PUT    /api/v1/assignments/{assignment_id}/reports/{student_id}/grade — TEACHER: chấm điểm
"""
from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentReportCreate, AssignmentReportResponse, GradeSubmission,
)
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["Bài tập"])


@router.get("", response_model=list[AssignmentResponse])
def list_assignments(
    class_id: str | None  = Query(None),
    course_id: str | None = Query(None),
    db: DbDep = None,
    _: CurrentUserDep = None,
):
    """Lấy danh sách bài tập."""
    return AssignmentService.list_assignments(db, class_id, course_id)


@router.post("", response_model=AssignmentResponse, status_code=201)
def create_assignment(data: AssignmentCreate, db: DbDep = None, _=Depends(require_role("TEACHER", "ADMIN"))):
    """Tạo bài tập mới. TEACHER hoặc ADMIN."""
    return AssignmentService.create_assignment(
        db, data.assignment_id, data.assignment_name, data.deadline,
        data.class_id, data.course_id, data.teacher_id, data.semester, data.link_url,
    )


# Phải đứng TRƯỚC /{assignment_id} để không bị che
@router.get("/my-submissions")
def get_my_submissions(db: DbDep = None, current_user: CurrentUserDep = None):
    """Sinh viên xem tất cả bài nộp của mình kèm điểm."""
    return AssignmentService.get_my_submissions(db, current_user.user_id)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem chi tiết bài tập."""
    return AssignmentService.get_assignment(db, assignment_id)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: str,
    data: AssignmentUpdate,
    db: DbDep = None,
    _=Depends(require_role("TEACHER", "ADMIN")),
):
    """Cập nhật bài tập. TEACHER hoặc ADMIN."""
    return AssignmentService.update_assignment(db, assignment_id, data.model_dump(exclude_none=True))


@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(assignment_id: str, db: DbDep = None, _=Depends(require_role("TEACHER", "ADMIN"))):
    """Xóa bài tập. TEACHER hoặc ADMIN."""
    AssignmentService.delete_assignment(db, assignment_id)


@router.get("/{assignment_id}/reports")
def get_assignment_reports(assignment_id: str, db: DbDep = None, _=Depends(require_role("TEACHER", "ADMIN"))):
    """Xem tất cả bài nộp của một bài tập kèm thông tin sinh viên. TEACHER và ADMIN."""
    return AssignmentService.get_reports(db, assignment_id)


@router.put("/{assignment_id}/reports/{student_id}/grade")
def grade_submission(
    assignment_id: str,
    student_id: str,
    data: GradeSubmission,
    db: DbDep = None,
    _=Depends(require_role("TEACHER", "ADMIN")),
):
    """Giáo viên chấm điểm bài nộp của sinh viên."""
    return AssignmentService.grade_submission(db, assignment_id, student_id, data.grade, data.feedback)


@router.post("/{assignment_id}/submit", response_model=AssignmentReportResponse, status_code=201)
def submit_assignment(
    assignment_id: str,
    data: AssignmentReportCreate,
    db: DbDep = None,
    current_user: CurrentUserDep = None,
):
    """Sinh viên nộp bài."""
    return AssignmentService.submit(
        db, current_user, assignment_id,
        data.student_id, data.class_id, data.lesson_id,
        data.link_url, data.submit_date,
    )
