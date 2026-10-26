"""
Router: Quản lý người dùng (Users)
Endpoints:
  GET    /api/v1/users              — ADMIN: danh sách users
  POST   /api/v1/users              — ADMIN: tạo user mới
  GET    /api/v1/users/{user_id}    — ADMIN hoặc chính user đó
  PUT    /api/v1/users/{user_id}    — ADMIN hoặc chính user đó
  DELETE /api/v1/users/{user_id}    — ADMIN: xóa user
  POST   /api/v1/users/{user_id}/roles — ADMIN: gán role
  DELETE /api/v1/users/{user_id}/roles/{role_id} — ADMIN: gỡ role
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.dependencies import get_db, get_current_user, require_role, DbDep, CurrentUserDep
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserRoleCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Quản lý người dùng"])


@router.get("", response_model=list[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Lấy danh sách tất cả users. Chỉ ADMIN."""
    return UserService.list_users(db, page, page_size)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Tạo user mới. Chỉ ADMIN."""
    return UserService.create_user(
        db, data.user_id, data.email, data.password,
        data.name, data.contact, data.birth
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: DbDep = None, current_user: CurrentUserDep = None):
    """Lấy thông tin user. ADMIN xem được tất cả, user thường chỉ xem mình."""
    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin user này")
    return UserService.get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    data: UserUpdate,
    db: DbDep = None,
    current_user: CurrentUserDep = None,
):
    """Cập nhật thông tin user. ADMIN hoặc chính user đó."""
    role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền sửa user này")
    return UserService.update_user(db, user_id, data.model_dump(exclude_none=True))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Xóa user. Chỉ ADMIN."""
    UserService.delete_user(db, user_id)


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
def assign_role(
    user_id: str,
    data: UserRoleCreate,
    db: DbDep = None,
    _=Depends(require_role("ADMIN")),
):
    """Gán role cho user. Chỉ ADMIN."""
    return UserService.assign_role(db, user_id, data.role_id)


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role(user_id: str, role_id: str, db: DbDep = None, _=Depends(require_role("ADMIN"))):
    """Gỡ role khỏi user. Chỉ ADMIN."""
    UserService.remove_role(db, user_id, role_id)
