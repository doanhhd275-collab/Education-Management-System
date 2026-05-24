#!/bin/bash
# =================================================================
# EMS - Script khởi động toàn bộ hệ thống
# Chạy: bash start.sh
# =================================================================

set -e  # Dừng nếu có lỗi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/venv"

echo "============================================"
echo "  EMS - Hệ Thống Quản Lý Đào Tạo"
echo "============================================"

# ── 1. Khởi động Database ────────────────────────────────────
echo ""
echo "[1/4] Khởi động PostgreSQL + Redis..."
docker compose up -d --wait 2>/dev/null || docker-compose up -d
echo "      ✓ Database sẵn sàng"

# Đợi PostgreSQL khởi động
sleep 3

# ── 2. Cài Python packages ───────────────────────────────────
echo ""
echo "[2/4] Cài Python packages..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install -r "$BACKEND_DIR/requirements.txt" -q
echo "      ✓ Python packages OK"

# ── 3. Khởi động Backend ─────────────────────────────────────
echo ""
echo "[3/4] Khởi động FastAPI Backend (port 8000)..."
cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "      ✓ Backend PID: $BACKEND_PID"
sleep 2

# ── 4. Khởi động Frontend ────────────────────────────────────
echo ""
echo "[4/4] Khởi động React Frontend (port 5173)..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "      Đang cài npm packages (lần đầu mất vài phút)..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "      ✓ Frontend PID: $FRONTEND_PID"

# ── Thông tin truy cập ───────────────────────────────────────
echo ""
echo "============================================"
echo "  ✅ Hệ thống đã khởi động!"
echo "============================================"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Database:  postgresql://localhost:5432/hust_ems"
echo ""
echo "  Tài khoản test:"
echo "    Admin:   admin@ems.edu.vn    / Admin@123"
echo "    Teacher: teacher1@ems.edu.vn / Admin@123"
echo "    Student: student1@ems.edu.vn / Admin@123"
echo ""
echo "  Nhấn Ctrl+C để dừng hệ thống"
echo "============================================"

# Đợi Ctrl+C
trap "echo ''; echo 'Đang tắt...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose down 2>/dev/null; exit 0" INT
wait
