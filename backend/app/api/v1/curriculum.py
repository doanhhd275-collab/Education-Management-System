"""
Router: Quản lý chương trình đào tạo (Curriculum)
Endpoints:
  GET    /api/v1/curriculum                                     — Danh sách chương trình
  POST   /api/v1/curriculum                                     — ADMIN: tạo chương trình
  GET    /api/v1/curriculum/{program_id}                        — Chi tiết + danh sách môn
  PUT    /api/v1/curriculum/{program_id}                        — ADMIN: cập nhật
  DELETE /api/v1/curriculum/{program_id}                        — ADMIN: xóa
  POST   /api/v1/curriculum/{program_id}/courses                — ADMIN: thêm môn
  DELETE /api/v1/curriculum/{program_id}/courses/{course_id}    — ADMIN: gỡ môn
"""
from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_role, DbDep, CurrentUserDep
from app.schemas.curriculum import (
    CurriculumCreate, CurriculumUpdate, CurriculumResponse,
    CurriculumCourseCreate, CurriculumCourseResponse,
)
from app.services.curriculum_service import CurriculumService

router = APIRouter(prefix="/curriculum", tags=["Chương trình đào tạo"])


@router.get("", response_model=list[CurriculumResponse])
def list_curriculum(db: DbDep = None, _: CurrentUserDep = None):
    """Lấy danh sách tất cả chương trình đào tạo."""
    return CurriculumService.list_curricula(db)


@router.post("", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED)
def create_curriculum(data: CurriculumCreate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Tạo chương trình đào tạo mới. Chỉ ADMIN."""
    return CurriculumService.create_curriculum(db, data.program_id, data.program_name)


@router.get("/{program_id}", response_model=CurriculumResponse)
def get_curriculum(program_id: str, db: DbDep = None, _: CurrentUserDep = None):
    """Xem chi tiết chương trình đào tạo kèm danh sách môn học."""
    return CurriculumService.get_curriculum(db, program_id)


@router.put("/{program_id}", response_model=CurriculumResponse)
def update_curriculum(program_id: str, data: CurriculumUpdate, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Cập nhật chương trình đào tạo. Chỉ ADMIN."""
    return CurriculumService.update_curriculum(db, program_id, data.program_name)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curriculum(program_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Xóa chương trình đào tạo. Chỉ ADMIN."""
    CurriculumService.delete_curriculum(db, program_id)


@router.post("/{program_id}/courses", response_model=CurriculumCourseResponse, status_code=201)
def add_course_to_curriculum(
    program_id: str,
    data: CurriculumCourseCreate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Thêm môn học vào chương trình đào tạo. Chỉ ADMIN."""
    return CurriculumService.add_course(db, program_id, data.course_id)


@router.delete("/{program_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_course_from_curriculum(program_id: str, course_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Gỡ môn học khỏi chương trình đào tạo. Chỉ ADMIN."""
    CurriculumService.remove_course(db, program_id, course_id)
