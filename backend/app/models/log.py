"""
models/log.py — ReportLog + SystemLog (Logging hệ thống)

ReportLog: lịch sử hành động người dùng (audit trail).
SystemLog: log kỹ thuật của hệ thống (errors, warnings, info).
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class ReportLog(Base):
    """
    ERD: LogID INT (PK, autoincrement), UserID, IP, Content VARCHAR(1000), TimeLog DATETIME.
    """
    __tablename__ = "report_logs"

    log_id   = Column("LogID",   Integer,    primary_key=True, autoincrement=True)
    user_id  = Column("UserID",  String(10), ForeignKey("users.UserID"), nullable=False)
    ip       = Column("IP",      String(20))
    content  = Column("Content", String(1000))
    time_log = Column("TimeLog", DateTime,   nullable=False)

    # relationships
    user = relationship("User", back_populates="report_logs")


class SystemLog(Base):
    """
    ERD: LogID VARCHAR(10) (PK), IP, Action VARCHAR(10), UserID, Content VARCHAR(1000), TimeLog DATETIME.
    """
    __tablename__ = "system_logs"

    log_id   = Column("LogID",   String(10),  primary_key=True)
    ip       = Column("IP",      String(20))
    action   = Column("Action",  String(10))
    user_id  = Column("UserID",  String(10),  ForeignKey("users.UserID"))
    content  = Column("Content", String(1000))
    time_log = Column("TimeLog", DateTime,    nullable=False)

    # relationships
    user = relationship("User", back_populates="system_logs")
