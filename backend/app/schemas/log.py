"""
Schemas cho ReportLog và SystemLog.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================
# REPORT LOG  (Audit trail hành động người dùng)
# PK: LogID INT autoincrement
# ============================================================

class ReportLogCreate(BaseModel):
    user_id: str            = Field(..., max_length=10)
    ip:      Optional[str] = Field(None, max_length=20)
    content: Optional[str] = Field(None, max_length=1000)
    # time_log tự động set tại DB / service layer


class ReportLogResponse(ReportLogCreate):
    log_id:   int
    time_log: datetime

    model_config = {"from_attributes": True}


class ReportLogFilter(BaseModel):
    """Query params để lọc log."""
    user_id:    Optional[str]      = None
    from_time:  Optional[datetime] = None
    to_time:    Optional[datetime] = None
    page:       int = Field(1,  ge=1)
    page_size:  int = Field(50, ge=1, le=200)


# ============================================================
# SYSTEM LOG  (Lỗi / cảnh báo kỹ thuật)
# PK: LogID VARCHAR(10)
# ============================================================

class SystemLogCreate(BaseModel):
    log_id:  str            = Field(..., max_length=10)
    ip:      Optional[str] = Field(None, max_length=20)
    action:  Optional[str] = Field(None, max_length=10,
                                   description="Ví dụ: ERROR, WARN, INFO")
    user_id: Optional[str] = Field(None, max_length=10)
    content: Optional[str] = Field(None, max_length=1000)
    # time_log tự động set tại DB / service layer


class SystemLogResponse(SystemLogCreate):
    time_log: datetime

    model_config = {"from_attributes": True}


class SystemLogFilter(BaseModel):
    action:    Optional[str]      = None
    user_id:   Optional[str]      = None
    from_time: Optional[datetime] = None
    to_time:   Optional[datetime] = None
    page:      int = Field(1,  ge=1)
    page_size: int = Field(50, ge=1, le=200)
