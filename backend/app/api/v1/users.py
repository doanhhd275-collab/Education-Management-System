"""
Router: Quản lý người dùng (Users)
Quyền truy cập:
  - ADMIN: toàn quyền (CRUD + gán role)
  - User thường: chỉ xem/sửa profile của mình

Endpoints:
  GET    /api/v1/users              — ADMIN: danh sách tất cả users
  POST   /api/v1/users              — ADMIN: tạo user mới
  GET    /api/v1/users/{user_id}    — ADMIN hoặc chính user đó
  PUT    /api/v1/users/{user_id}    — ADMIN hoặc chính user đó
  DELETE /api/v1/users/{user_id}    — ADMIN: xóa user
  POST   /api/v1/users/{user_id}/roles — ADMIN: gán role cho user
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, get_current_user, require_role
from app.core.security import hash_password
from app.models.user import User, UserRole, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserRoleCreate

router = APIRouter(prefix="/users", tags=["Quản lý người dùng"])


def _load_user_with_roles(db: Session, user_id: str) -> User | None:
    """Helper: load User + user_roles (eager) để tránh lazy-load lỗi."""
    return (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .filter(User.user_id == user_id)
        .first()
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))   # Chỉ ADMIN
):
    """Lấy danh sách tất cả users (eager load roles). Chỉ ADMIN."""
    offset = (page - 1) * page_size
    users = (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Tạo user mới. Chỉ ADMIN."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{data.email}' đã được sử dụng"
        )
    if db.query(User).filter(User.user_id == data.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã người dùng '{data.user_id}' đã tồn tại"
        )

    new_user = User(
        user_id  = data.user_id,
        email    = data.email,
        password = hash_password(data.password),
        contact  = data.contact,
        birth    = data.birth,
        name     = data.name,
    )
    db.add(new_user)
    db.commit()

    # Reload với eager load để trả về đầy đủ
    return _load_user_with_roles(db, new_user.user_id)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy thông tin user. ADMIN xem được tất cả, user thường chỉ xem mình."""
    # Lấy role_id của current_user từ DB
    current_role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in current_role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin user này")

    user = _load_user_with_roles(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật thông tin user. ADMIN hoặc chính user đó."""
    current_role_ids = [ur.role_id for ur in current_user.user_roles]
    if "ADMIN" not in current_role_ids and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền sửa user này")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)

    db.commit()
    return _load_user_with_roles(db, user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Xóa user. Chỉ ADMIN."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    db.delete(user)
    db.commit()


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
def assign_role(
    user_id: str,
    data: UserRoleCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Gán role cho user. Chỉ ADMIN."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    role = db.query(Role).filter(Role.role_id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{data.role_id}' không tồn tại")

    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == data.role_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User đã có role này rồi")

    db.add(UserRole(user_id=user_id, role_id=data.role_id))
    db.commit()
    return {"message": f"Gán role '{role.role_name}' cho '{user.name}' thành công"}


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role(
    user_id: str,
    role_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Gỡ role khỏi user. Chỉ ADMIN."""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User không có role này")
    db.delete(user_role)
    db.commit()
