"""
Router: Quản lý bài tập (Assignments) + bài nộp (AssignmentReports)
Endpoints:
  GET    /api/v1/assignments                            — Danh sách bài tập (theo lớp)
  POST   /api/v1/assignments                            — TEACHER: tạo bài tập
  GET    /api/v1/assignments/{assignment_id}            — Chi tiết bài tập
  PUT    /api/v1/assignments/{assignment_id}            — TEACHER: cập nhật
  DELETE /api/v1/assignments/{assignment_id}            — TEACHER/ADMIN: xóa

  GET    /api/v1/assignments/{assignment_id}/reports    — TEACHER: xem bài nộp
  POST   /api/v1/assignments/{assignment_id}/submit     — STUDENT: nộp bài
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Assignment, AssignmentReport, Teacher, Student, User
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentReportCreate, AssignmentReportResponse
)

router = APIRouter(prefix="/assignments", tags=["Bài tập"])


@router.get("", response_model=list[AssignmentResponse])
def list_assignments(
    class_id: str | None  = Query(None, description="Lọc theo lớp"),
    course_id: str | None = Query(None, description="Lọc theo môn"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Lấy danh sách bài tập."""
    query = db.query(Assignment)

    if class_id:
        query = query.filter(Assignment.class_id == class_id)
    if course_id:
        query = query.filter(Assignment.course_id == course_id)

    return query.all()


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """Tạo bài tập mới. TEACHER hoặc ADMIN."""
    if db.query(Assignment).filter(Assignment.assignment_id == data.assignment_id).first():
        raise HTTPException(status_code=400, detail=f"AssignmentID '{data.assignment_id}' đã tồn tại")

    assignment = Assignment(
        assignment_id=data.assignment_id,
        assignment_name=data.assignment_name,
        deadline=data.deadline,
        class_id=data.class_id,
        course_id=data.course_id,
        teacher_id=data.teacher_id,
        semester=data.semester,
        link_url=data.link_url,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem chi tiết bài tập."""
    assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: str,
    data: AssignmentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """Cập nhật bài tập. TEACHER hoặc ADMIN."""
    assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """Xóa bài tập. TEACHER hoặc ADMIN."""
    assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")
    db.delete(assignment)
    db.commit()


# ── Bài nộp (AssignmentReport) ──────────────────────────────

@router.get("/{assignment_id}/reports")
def get_assignment_reports(
    assignment_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("TEACHER", "ADMIN"))
):
    """Xem tất cả bài nộp của một bài tập kèm thông tin sinh viên. TEACHER và ADMIN."""
    from app.models.user import Student, User as UserModel
    from sqlalchemy.orm import joinedload
    if not db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")

    reports = (
        db.query(AssignmentReport)
        .options(joinedload(AssignmentReport.student).joinedload(Student.user))
        .filter(AssignmentReport.assignment_id == assignment_id)
        .all()
    )

    result = []
    for r in reports:
        student_name = r.student.user.name if r.student and r.student.user else None
        result.append({
            "assignment_id": r.assignment_id,
            "student_id":    r.student_id,
            "student_name":  student_name,
            "class_id":      r.class_id,
            "lesson_id":     r.lesson_id,
            "submit_date":   r.submit_date,
            "link_url":      r.link_url,
        })
    return result


@router.post("/{assignment_id}/submit", response_model=AssignmentReportResponse, status_code=201)
def submit_assignment(
    assignment_id: str,
    data: AssignmentReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sinh viên nộp bài.
    STUDENT chỉ nộp được cho chính mình.
    """
    role_ids = [ur.role_id for ur in current_user.user_roles]

    # Sinh viên chỉ nộp cho bản thân
    if "STUDENT" in role_ids and "ADMIN" not in role_ids:
        if data.student_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ được nộp bài cho bản thân")

    # Kiểm tra bài tập tồn tại
    assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập")

    # Kiểm tra đã nộp chưa
    existing = db.query(AssignmentReport).filter(
        AssignmentReport.assignment_id == assignment_id,
        AssignmentReport.student_id == data.student_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã nộp bài này rồi")

    report = AssignmentReport(
        assignment_id=assignment_id,
        class_id=data.class_id,
        student_id=data.student_id,
        lesson_id=data.lesson_id,
        link_url=data.link_url,
        submit_date=data.submit_date or datetime.now(timezone.utc)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        "assignment_id": report.assignment_id,
        "student_id":    report.student_id,
        "student_name":  None,
        "class_id":      report.class_id,
        "lesson_id":     report.lesson_id,
        "submit_date":   report.submit_date,
        "link_url":      report.link_url,
    }
