"""
Router: Quản lý chương trình đào tạo (Curriculum)
Endpoints:
  GET    /api/v1/curriculum                               — Danh sách chương trình
  POST   /api/v1/curriculum                               — ADMIN: tạo chương trình
  GET    /api/v1/curriculum/{program_id}                  — Chi tiết + danh sách môn
  PUT    /api/v1/curriculum/{program_id}                  — ADMIN: cập nhật
  DELETE /api/v1/curriculum/{program_id}                  — ADMIN: xóa
  POST   /api/v1/curriculum/{program_id}/courses          — ADMIN: thêm môn vào chương trình
  DELETE /api/v1/curriculum/{program_id}/courses/{course_id} — ADMIN: gỡ môn
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Curriculum, CurriculumCourse, Course, User
from app.schemas.curriculum import (
    CurriculumCreate, CurriculumUpdate, CurriculumResponse,
    CurriculumCourseCreate, CurriculumCourseResponse
)

router = APIRouter(prefix="/curriculum", tags=["Chương trình đào tạo"])


@router.get("", response_model=list[CurriculumResponse])
def list_curriculum(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)  # Mọi user đăng nhập đều xem được
):
    """Lấy danh sách tất cả chương trình đào tạo."""
    programs = db.query(Curriculum).all()
    return programs


@router.post("", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED)
def create_curriculum(
    data: CurriculumCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Tạo chương trình đào tạo mới. Chỉ ADMIN."""
    if db.query(Curriculum).filter(Curriculum.program_id == data.program_id).first():
        raise HTTPException(status_code=400, detail=f"ProgramID '{data.program_id}' đã tồn tại")

    program = Curriculum(program_id=data.program_id, program_name=data.program_name)
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/{program_id}", response_model=CurriculumResponse)
def get_curriculum(
    program_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem chi tiết chương trình đào tạo kèm danh sách môn học."""
    program = (
        db.query(Curriculum)
        .options(joinedload(Curriculum.curriculum_courses).joinedload(CurriculumCourse.course))
        .filter(Curriculum.program_id == program_id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
    return program


@router.put("/{program_id}", response_model=CurriculumResponse)
def update_curriculum(
    program_id: str,
    data: CurriculumUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Cập nhật chương trình đào tạo. Chỉ ADMIN."""
    program = db.query(Curriculum).filter(Curriculum.program_id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")

    if data.program_name:
        program.program_name = data.program_name

    db.commit()
    db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curriculum(
    program_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Xóa chương trình đào tạo. Chỉ ADMIN."""
    program = db.query(Curriculum).filter(Curriculum.program_id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
    db.delete(program)
    db.commit()


@router.post("/{program_id}/courses", response_model=CurriculumCourseResponse, status_code=201)
def add_course_to_curriculum(
    program_id: str,
    data: CurriculumCourseCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Thêm môn học vào chương trình đào tạo. Chỉ ADMIN."""
    # Kiểm tra chương trình và môn học tồn tại
    if not db.query(Curriculum).filter(Curriculum.program_id == program_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
    if not db.query(Course).filter(Course.course_id == data.course_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")

    # Kiểm tra chưa có trong chương trình
    existing = db.query(CurriculumCourse).filter(
        CurriculumCourse.program_id == program_id,
        CurriculumCourse.course_id == data.course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Môn học đã có trong chương trình này rồi")

    cc = CurriculumCourse(program_id=program_id, course_id=data.course_id)
    db.add(cc)
    db.commit()
    db.refresh(cc)
    return cc


@router.delete("/{program_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_course_from_curriculum(
    program_id: str,
    course_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Gỡ môn học khỏi chương trình đào tạo. Chỉ ADMIN."""
    cc = db.query(CurriculumCourse).filter(
        CurriculumCourse.program_id == program_id,
        CurriculumCourse.course_id == course_id
    ).first()
    if not cc:
        raise HTTPException(status_code=404, detail="Môn học không có trong chương trình này")
    db.delete(cc)
    db.commit()
