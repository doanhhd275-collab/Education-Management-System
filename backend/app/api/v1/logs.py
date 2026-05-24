"""
Router: Quản lý hệ thống - Logs (System Management)
Chỉ ADMIN mới được truy cập.

Endpoints:
  GET  /api/v1/logs/report   — Xem report logs (hành động người dùng)
  GET  /api/v1/logs/system   — Xem system logs (lỗi kỹ thuật)
  POST /api/v1/logs/system   — Ghi system log
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.dependencies import get_db, require_role
from app.models.user import ReportLog, SystemLog
from app.schemas.log import (
    ReportLogResponse,
    SystemLogCreate, SystemLogResponse
)

router = APIRouter(prefix="/logs", tags=["Quản lý hệ thống - Logs"])


@router.get("/report", response_model=list[ReportLogResponse])
def get_report_logs(
    user_id: str | None       = Query(None, description="Lọc theo user"),
    from_time: datetime | None = Query(None, description="Từ thời điểm"),
    to_time: datetime | None   = Query(None, description="Đến thời điểm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))  # Chỉ ADMIN
):
    """Xem lịch sử hành động người dùng (ReportLog). Chỉ ADMIN."""
    query = db.query(ReportLog)

    if user_id:
        query = query.filter(ReportLog.user_id == user_id)
    if from_time:
        query = query.filter(ReportLog.time_log >= from_time)
    if to_time:
        query = query.filter(ReportLog.time_log <= to_time)

    # Sắp xếp mới nhất trước
    logs = (
        query
        .order_by(ReportLog.time_log.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return logs


@router.get("/system", response_model=list[SystemLogResponse])
def get_system_logs(
    action: str | None        = Query(None, description="ERROR | WARN | INFO"),
    user_id: str | None       = Query(None, description="Lọc theo user"),
    from_time: datetime | None = Query(None, description="Từ thời điểm"),
    to_time: datetime | None   = Query(None, description="Đến thời điểm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Xem system logs (lỗi kỹ thuật, cảnh báo). Chỉ ADMIN."""
    query = db.query(SystemLog)

    if action:
        query = query.filter(SystemLog.action == action.upper())
    if user_id:
        query = query.filter(SystemLog.user_id == user_id)
    if from_time:
        query = query.filter(SystemLog.time_log >= from_time)
    if to_time:
        query = query.filter(SystemLog.time_log <= to_time)

    logs = (
        query
        .order_by(SystemLog.time_log.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return logs


@router.post("/system", response_model=SystemLogResponse, status_code=201)
def create_system_log(
    data: SystemLogCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Ghi system log thủ công. Chỉ ADMIN."""
    from datetime import timezone
    log = SystemLog(
        log_id=data.log_id,
        ip=data.ip,
        action=data.action,
        user_id=data.user_id,
        content=data.content,
        time_log=datetime.now(timezone.utc)
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
