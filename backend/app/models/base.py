"""
Định nghĩa Base class duy nhất dùng chung cho toàn bộ SQLAlchemy models.
Import file này thay vì định nghĩa Base ở nhiều nơi.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
