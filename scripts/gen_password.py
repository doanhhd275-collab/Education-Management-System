#!/usr/bin/env python3
"""
Script tạo bcrypt hash cho mật khẩu.
Chạy: python3 scripts/gen_password.py
Dùng để cập nhật seed data trong init.sql
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

passwords = ["Admin@123"]
for p in passwords:
    hashed = pwd_context.hash(p)
    print(f"Plain: {p}")
    print(f"Hash:  {hashed}")
    print(f"Verify: {pwd_context.verify(p, hashed)}")
    print()
