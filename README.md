# 🎓 EMS — Education Management System

> Hệ thống quản lý đào tạo toàn diện xây dựng trên **FastAPI · React · PostgreSQL**

---

## 📑 Mục lục

- [Tổng quan](#-tổng-quan)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Hướng dẫn cài đặt](#-hướng-dẫn-cài-đặt)
- [Địa chỉ truy cập](#-địa-chỉ-truy-cập)
- [Tài khoản mặc định](#-tài-khoản-mặc-định)
- [Danh sách API](#-danh-sách-api)
- [Các tính năng chính](#-các-tính-năng-chính)
- [Xử lý sự cố](#-xử-lý-sự-cố)

---

## 🌟 Tổng quan

**EMS (Education Management System)** là một ứng dụng web quản lý đào tạo đầy đủ chức năng, hỗ trợ ba vai trò người dùng: **Quản trị viên**, **Giáo viên** và **Sinh viên**.

Hệ thống bao gồm các nghiệp vụ cốt lõi:

- 🏫 Quản lý chương trình đào tạo, môn học, lớp học
- 👩‍🏫 Quản lý giáo viên và sinh viên
- 📝 Đăng ký học, điểm danh, bài tập
- 📄 Quản lý tài liệu học tập
- 📊 Chấm điểm và thống kê
- 🔒 Xác thực JWT, phân quyền theo vai trò (RBAC)
- 🗂️ Nhật ký hệ thống (System Logs)

---

## 🛠️ Công nghệ sử dụng

### Backend
| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| FastAPI | 0.115.5 | Web framework ASGI |
| Uvicorn | 0.32.1 | ASGI server |
| SQLAlchemy | 2.0.36 | ORM |
| Alembic | 1.14.0 | Database migration |
| Pydantic | 2.10.3 | Data validation |
| python-jose | 3.3.0 | JWT authentication |
| passlib[bcrypt] | 1.7.4 | Password hashing |
| psycopg2-binary | 2.9.10 | PostgreSQL driver |

### Frontend
| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| React | 18.3.1 | UI framework |
| Vite | 5.2.0 | Build tool |
| React Router DOM | 6.23.1 | Client-side routing |
| Axios | 1.6.8 | HTTP client |

### Infrastructure
| Công nghệ | Phiên bản | Mục đích |
|---|---|---|
| PostgreSQL | 15-alpine | Cơ sở dữ liệu chính |
| Redis | 7-alpine | Cache |
| Docker / Docker Compose | — | Container hóa |

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT BROWSER                     │
│                React 18 + Vite (port 5173)              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST API
┌────────────────────────▼────────────────────────────────┐
│                    BACKEND API                          │
│            FastAPI + Uvicorn (port 8000)                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  API Router │  │   Services   │  │  Auth (JWT)   │  │
│  │  (12 routes)│  │  (Business)  │  │  + RBAC       │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│  ┌────────────────────────────────────────────────────┐ │
│  │        SQLAlchemy ORM + Pydantic Schemas           │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴──────────────┐
        │                               │
┌───────▼────────┐             ┌────────▼───────┐
│  PostgreSQL 15 │             │   Redis 7      │
│  (port 5432)   │             │   (port 6379)  │
└────────────────┘             └────────────────┘
```

---

## 📁 Cấu trúc thư mục

```
Education-Management-System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/                   # API endpoints
│   │   │       ├── auth.py           # Đăng nhập / token
│   │   │       ├── users.py          # Quản lý người dùng
│   │   │       ├── students.py       # Quản lý sinh viên
│   │   │       ├── teachers.py       # Quản lý giáo viên
│   │   │       ├── curriculum.py     # Chương trình đào tạo
│   │   │       ├── courses.py        # Môn học
│   │   │       ├── classes.py        # Lớp học
│   │   │       ├── enrollments.py    # Đăng ký học
│   │   │       ├── documents.py      # Tài liệu
│   │   │       ├── assignments.py    # Bài tập
│   │   │       ├── attendance.py     # Điểm danh
│   │   │       └── logs.py           # Nhật ký hệ thống
│   │   ├── core/                     # Config, DB, Security
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Business logic
│   │   └── main.py                   # App entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── api/                      # Axios API clients
│   │   ├── components/               # Layout, ProtectedRoute
│   │   ├── context/                  # AuthContext (React Context)
│   │   ├── pages/
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Students/
│   │   │   ├── Teachers/
│   │   │   ├── Users/
│   │   │   ├── Courses/
│   │   │   ├── Classes/
│   │   │   ├── Curriculum/
│   │   │   ├── Enrollment/
│   │   │   ├── Documents/
│   │   │   ├── Assignments/
│   │   │   ├── Attendance/
│   │   │   ├── Grading/
│   │   │   ├── Profile/
│   │   │   └── Logs/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── infrastructure/
│   └── db/
│       └── init.sql                  # SQL seed data
├── scripts/
│   └── seed_data.py                  # Script seed dữ liệu
├── docker-compose.yml                # PostgreSQL + Redis
├── start.sh                          # Script khởi động 1 lệnh
└── README.md
```

---

## 💻 Yêu cầu hệ thống

| Công cụ | Phiên bản tối thiểu |
|---|---|
| Docker | 24.0+ |
| Docker Compose | 2.0+ |
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

## 🚀 Hướng dẫn cài đặt

### ⚡ Cách 1: Chạy tự động (khuyến nghị)

```bash
chmod +x start.sh
bash start.sh
```

Script sẽ tự động khởi động database, cài dependencies, seed dữ liệu và chạy cả backend lẫn frontend.

---

### 🔧 Cách 2: Chạy thủ công từng bước

#### Bước 1 — Khởi động Database (PostgreSQL + Redis)

```bash
docker compose up -d
```

Kiểm tra database đã sẵn sàng:

```bash
docker compose ps
```

#### Bước 2 — Thiết lập môi trường Python

```bash
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

pip install -r backend/requirements.txt
```

#### Bước 3 — Chạy Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Bước 4 — Seed dữ liệu mẫu *(chỉ chạy lần đầu)*

```bash
# Mở terminal mới
source venv/bin/activate
python scripts/seed_data.py
```

#### Bước 5 — Chạy Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Địa chỉ truy cập

| Service | URL |
|---|---|
| 🖥️ Frontend App | http://localhost:5173 |
| ⚙️ Backend API | http://localhost:8000 |
| 📘 Swagger UI (API Docs) | http://localhost:8000/docs |
| 📗 ReDoc | http://localhost:8000/redoc |
| 🗄️ Database | `postgresql://ems_admin:ems_password123@localhost:5432/hust_ems` |
| 🔴 Redis | `redis://localhost:6379` |

---

## 🔑 Tài khoản mặc định

| Email | Mật khẩu | Vai trò |
|---|---|---|
| `admin@ems.edu.vn` | `Admin@123` | 👑 Quản trị viên |
| `teacher1@ems.edu.vn` | `Admin@123` | 👩‍🏫 Giáo viên |
| `teacher2@ems.edu.vn` | `Admin@123` | 👩‍🏫 Giáo viên |
| `student1@ems.edu.vn` | `Admin@123` | 🎓 Sinh viên |
| `student2@ems.edu.vn` | `Admin@123` | 🎓 Sinh viên |

> ⚠️ **Lưu ý**: Đổi mật khẩu mặc định trước khi triển khai lên môi trường production.

---

## 📋 Danh sách API

### Phân quyền theo vai trò

| Ký hiệu | Vai trò |
|---|---|
| 🌐 `Public` | Không cần xác thực |
| 👑 `ADMIN` | Chỉ quản trị viên |
| 👩‍🏫 `TEACHER` | Giáo viên |
| 🎓 `STUDENT` | Sinh viên |
| ✅ `All` | Tất cả người dùng đã đăng nhập |

### Bảng API

| Module | Endpoint | Phương thức | Quyền | Mô tả |
|---|---|---|---|---|
| **Auth** | `/api/v1/auth/login` | POST | 🌐 Public | Đăng nhập, lấy JWT token |
| **Auth** | `/api/v1/auth/me` | GET | ✅ All | Lấy thông tin người dùng hiện tại |
| **Users** | `/api/v1/users` | GET / POST | 👑 ADMIN | Danh sách & tạo người dùng |
| **Users** | `/api/v1/users/{id}` | GET / PUT / DELETE | 👑 ADMIN | Chi tiết, cập nhật, xóa |
| **Students** | `/api/v1/students` | GET / POST | 👑 ADMIN, 👩‍🏫 TEACHER | Danh sách & tạo sinh viên |
| **Students** | `/api/v1/students/{id}` | GET / PUT / DELETE | 👑 ADMIN | Chi tiết, cập nhật, xóa |
| **Teachers** | `/api/v1/teachers` | GET / POST | 👑 ADMIN | Danh sách & tạo giáo viên |
| **Teachers** | `/api/v1/teachers/{id}` | GET / PUT / DELETE | 👑 ADMIN | Chi tiết, cập nhật, xóa |
| **Curriculum** | `/api/v1/curriculum` | GET / POST | ✅ All | Chương trình đào tạo |
| **Courses** | `/api/v1/courses` | GET / POST | ✅ All | Môn học |
| **Classes** | `/api/v1/classes` | GET / POST | ✅ All | Lớp học |
| **Enrollments** | `/api/v1/enrollments` | GET / POST | ✅ All | Đăng ký học |
| **Documents** | `/api/v1/documents` | GET / POST | ✅ All | Tài liệu học tập |
| **Assignments** | `/api/v1/assignments` | GET / POST | ✅ All | Bài tập |
| **Attendance** | `/api/v1/attendance` | GET / POST | ✅ All | Điểm danh |
| **Logs** | `/api/v1/logs` | GET | 👑 ADMIN | Nhật ký hệ thống |

> 📘 Xem tài liệu API đầy đủ tại [Swagger UI](http://localhost:8000/docs)

---

## ✨ Các tính năng chính

### 🔒 Bảo mật
- Xác thực JWT (JSON Web Token)
- Phân quyền theo vai trò (RBAC): Admin / Teacher / Student
- Mật khẩu băm bằng bcrypt
- Protected routes trên frontend

### 🗄️ Dữ liệu
- ORM với SQLAlchemy 2.0 (async-ready)
- Migration database bằng Alembic
- Seed dữ liệu mẫu tự động
- PostgreSQL 15 với persistent volume

### 🖥️ Giao diện
- SPA (Single Page Application) với React 18
- Routing phía client với React Router v6
- Responsive layout
- 15 trang quản lý khác nhau

### ⚡ Hiệu năng
- Redis cache layer
- ASGI server với Uvicorn
- Vite cho frontend build cực nhanh

---

## 🔧 Xử lý sự cố

### ❌ Lỗi "Module not found" hoặc `ImportError`

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

### ❌ Lỗi kết nối Database

```bash
# Khởi động lại container
docker compose down && docker compose up -d

# Kiểm tra log database
docker logs hust_ems_db
```

### ❌ Lỗi CORS

Kiểm tra file `backend/app/main.py`, đảm bảo `allow_origins` chứa:

```python
allow_origins=["http://localhost:5173"]
```

### ❌ Frontend không kết nối được API

Kiểm tra file `frontend/src/api/` — đảm bảo `baseURL` trỏ đúng về `http://localhost:8000`.

### ❌ Port đã được sử dụng

```bash
# Tìm process đang dùng port 8000
lsof -i :8000
kill -9 <PID>

# Tìm process đang dùng port 5173
lsof -i :5173
kill -9 <PID>
```

---

## 📄 Giấy phép

Dự án được phát triển phục vụ mục đích học tập và nghiên cứu.

---

<div align="center">
  <strong>EMS — Education Management System</strong><br/>
  FastAPI · React · PostgreSQL · Redis · Docker
</div>