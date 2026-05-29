# 🎓 Education Management System (EMS)

> **Hệ thống Quản lý Giáo dục** — Nền tảng toàn diện quản lý học tập, giảng dạy và đào tạo đại học.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docs.docker.com/compose/)

---

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng](#tính-năng)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cài đặt & Khởi động](#cài-đặt--khởi-động)
- [Tài khoản mặc định](#tài-khoản-mặc-định)
- [API Endpoints](#api-endpoints)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Deploy Production](#deploy-production)

---

## Tổng quan

EMS là hệ thống quản lý giáo dục được xây dựng theo kiến trúc **REST API + SPA**, gồm:

- **Backend**: FastAPI (Python) + SQLAlchemy + PostgreSQL
- **Frontend**: React 18 + Vite + Vanilla CSS (dark mode premium)
- **Auth**: JWT Bearer Token (access + refresh)
- **DB**: PostgreSQL (local Docker / Render Cloud)

---

## Tính năng

### 👥 Theo phân quyền

#### 🛡️ Admin (Quản trị viên)
| Tính năng | Mô tả |
|---|---|
| Quản lý người dùng | Tạo, sửa, xóa user; gán role |
| Quản lý sinh viên | Xem danh sách, thông tin học vụ |
| Quản lý giáo viên | Xem danh sách giáo viên |
| Quản lý môn học | CRUD môn học |
| Quản lý lớp học | Tạo lớp, gán giáo viên, đặt lịch học, phòng học |
| Chương trình đào tạo | Quản lý chương trình, học phần |
| Nhật ký hệ thống | Xem log hoạt động, báo cáo |

#### 👨‍🏫 Giáo viên
| Tính năng | Mô tả |
|---|---|
| Thời khóa biểu | Xem lịch dạy theo thứ/tiết/phòng (dạng lưới + danh sách) |
| Lớp học | Xem danh sách lớp mình phụ trách |
| Điểm danh | Tạo buổi học, điểm danh sinh viên |
| Nhập điểm | Nhập điểm thành phần, giữa kỳ, cuối kỳ |
| Bài tập | Tạo bài tập, xem bài nộp của sinh viên (link URL) |
| Tài liệu | Upload/chia sẻ tài liệu học tập |

#### 🎓 Sinh viên
| Tính năng | Mô tả |
|---|---|
| Thời khóa biểu | Xem lịch học theo thứ/tiết/phòng |
| Đăng ký học | Đăng ký / hủy đăng ký lớp học |
| Điểm danh | Xem lịch sử điểm danh theo từng lớp |
| Bài tập | Nộp bài tập qua link URL |
| Tài liệu | Xem tài liệu môn học |
| Xem điểm | Xem điểm các môn học |

---

## Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  Vite + React 18 + React Router + Context API           │
│  Port: 5173 (dev) / 80 (prod via Nginx)                 │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST (axios)
┌─────────────────────▼───────────────────────────────────┐
│                    BACKEND (FastAPI)                      │
│  Python 3.12 + SQLAlchemy + JWT + Uvicorn               │
│  Port: 8000                                              │
│  /api/v1/*                                               │
└─────────────────────┬───────────────────────────────────┘
                      │ SQLAlchemy ORM
┌─────────────────────▼───────────────────────────────────┐
│                   DATABASE (PostgreSQL)                   │
│  Port: 5432                                              │
│  Docker: hust_ems_db                                     │
└─────────────────────────────────────────────────────────┘
```

### 📊 Mô hình dữ liệu chính

```
users ──┬── students (1:1)
        ├── teachers (1:1)
        └── user_roles ── roles

courses ── classes ──┬── teacher_classes ── teachers
                     ├── enrollments ── students
                     ├── assignments ── assignment_reports
                     ├── lesson_reports (điểm danh)
                     └── grades
```

---

## Cài đặt & Khởi động

### Yêu cầu
- Docker & Docker Compose
- Python 3.12+
- Node.js 18+

### 1. Clone dự án
```bash
git clone https://github.com/doanhhd275-collab/Education-Management-System.git
cd Education-Management-System
```

### 2. Khởi động Database (Docker)
```bash
docker-compose up -d
```
> PostgreSQL chạy tại `localhost:5432`, DB: `hust_ems`, User: `ems_admin`, Pass: `ems_password123`

### 3. Backend
```bash
# Tạo và kích hoạt virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r backend/requirements.txt

# Tạo file .env
cp backend/.env.example backend/.env
# Chỉnh sửa DATABASE_URL nếu cần

# Chạy server (tự động tạo bảng + migrate + seed dữ liệu)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Mở trình duyệt
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 6. Script tự động (Linux)
```bash
chmod +x start.sh
./start.sh
```

---

## Tài khoản mặc định

> Mật khẩu mặc định: **`Admin@123`**

| Role | Email | Ghi chú |
|---|---|---|
| Admin | `admin@ems.edu.vn` | Toàn quyền hệ thống |
| Giáo viên | `teacher1@ems.edu.vn` | Giảng viên mẫu |
| Giáo viên | `teacher2@ems.edu.vn` | Giảng viên mẫu |
| Sinh viên | `student1@ems.edu.vn` | Sinh viên mẫu (SV001) |
| Sinh viên | `student2@ems.edu.vn` | Sinh viên mẫu |

---

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### 🔐 Authentication
| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/auth/login` | Đăng nhập, nhận JWT |
| `POST` | `/auth/logout` | Đăng xuất |
| `GET` | `/auth/me` | Thông tin user hiện tại |

### 👥 Users
| Method | Endpoint | Mô tả | Role |
|---|---|---|---|
| `GET` | `/users` | Danh sách users | ADMIN |
| `POST` | `/users` | Tạo user mới | ADMIN |
| `PUT` | `/users/{id}` | Cập nhật user | ADMIN |
| `DELETE` | `/users/{id}` | Xóa user | ADMIN |

### 🎓 Students
| Method | Endpoint | Mô tả | Role |
|---|---|---|---|
| `GET` | `/students` | Danh sách sinh viên | ADMIN, TEACHER |
| `GET` | `/students/{id}` | Chi tiết sinh viên | ADMIN, TEACHER |
| `PUT` | `/students/{id}` | Cập nhật thông tin | ADMIN |

### 👨‍🏫 Teachers
| Method | Endpoint | Mô tả | Role |
|---|---|---|---|
| `GET` | `/teachers` | Danh sách giáo viên | ADMIN |
| `GET` | `/teachers/me` | Thông tin GV đang đăng nhập | TEACHER |
| `GET` | `/teachers/{id}/classes` | Lớp phụ trách | ADMIN, TEACHER |

### 🏗️ Classes
| Method | Endpoint | Mô tả | Role |
|---|---|---|---|
| `GET` | `/classes` | Danh sách lớp học | ADMIN, TEACHER, STUDENT |
| `POST` | `/classes` | Tạo lớp học | **ADMIN** |
| `GET` | `/classes/{course_id}/{class_id}` | Chi tiết lớp | ADMIN, TEACHER, STUDENT |
| `PUT` | `/classes/{course_id}/{class_id}` | Cập nhật lớp — lịch học, phòng học | **ADMIN** |
| `DELETE` | `/classes/{course_id}/{class_id}` | Xóa lớp | **ADMIN** |
| `POST` | `/classes/{course_id}/{class_id}/teachers` | Gán giáo viên vào lớp | **ADMIN** |
| `GET` | `/classes/timetable/teacher` | Xem thời khóa biểu (chỉ đọc) | TEACHER |
| `GET` | `/classes/timetable/student` | Xem thời khóa biểu (chỉ đọc) | STUDENT |

> ⚠️ **Lưu ý**: Giáo viên **không có quyền** xếp lịch học, đặt phòng, hay tạo/xóa lớp. Tất cả thao tác ghi trên lớp học chỉ do **Admin** thực hiện.


### 📝 Enrollments
| Method | Endpoint | Mô tả | Role |
|---|---|---|---|
| `GET` | `/enrollments` | Danh sách đăng ký | ADMIN, STUDENT |
| `POST` | `/enrollments` | Đăng ký lớp học | STUDENT |
| `DELETE` | `/enrollments/{id}` | Hủy đăng ký | STUDENT |

### ✅ Attendance
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/attendance/class/{class_id}` | Lịch sử điểm danh |
| `POST` | `/attendance` | Tạo buổi điểm danh |
| `PUT` | `/attendance/{id}` | Cập nhật điểm danh |

### 📊 Grading
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/grading/{course_id}/{class_id}` | Bảng điểm lớp |
| `POST/PUT` | `/grading` | Nhập/cập nhật điểm |

### 📚 Assignments
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/assignments` | Danh sách bài tập |
| `POST` | `/assignments` | Tạo bài tập |
| `POST` | `/assignments/{id}/submit` | Nộp bài (link URL) |
| `GET` | `/assignments/{id}/submissions` | Xem bài nộp |

---

## Cấu trúc dự án

```
Education-Management-System/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/             # Endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── classes.py      # Lớp học + Thời khóa biểu
│   │   │   ├── users.py        # Quản lý người dùng
│   │   │   ├── students.py     # Sinh viên
│   │   │   ├── teachers.py     # Giáo viên
│   │   │   ├── courses.py      # Môn học
│   │   │   ├── curriculum.py   # Chương trình đào tạo
│   │   │   ├── enrollments.py  # Đăng ký học
│   │   │   ├── attendance.py   # Điểm danh
│   │   │   ├── assignments.py  # Bài tập
│   │   │   ├── documents.py    # Tài liệu
│   │   │   ├── logs.py         # Nhật ký hệ thống
│   │   │   └── grading.py      # Điểm số (nếu có)
│   │   ├── core/
│   │   │   ├── database.py     # SQLAlchemy engine/session
│   │   │   ├── dependencies.py # get_db, get_current_user, require_role
│   │   │   ├── security.py     # JWT, bcrypt
│   │   │   └── seed.py         # Seed dữ liệu mặc định
│   │   ├── models/
│   │   │   └── user.py         # Tất cả ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── main.py             # FastAPI app, lifespan, migrations
│   ├── requirements.txt
│   └── .env                    # DATABASE_URL, JWT_SECRET_KEY, etc.
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/index.js        # Axios API client
│   │   ├── context/
│   │   │   └── AuthContext.jsx # Auth state management
│   │   ├── components/
│   │   │   └── Layout/         # Sidebar, Layout, ProtectedRoute
│   │   ├── pages/
│   │   │   ├── Dashboard/      # Tổng quan
│   │   │   ├── Classes/        # Quản lý lớp học (Admin)
│   │   │   ├── Timetable/      # Thời khóa biểu (GV + SV)
│   │   │   ├── Attendance/     # Điểm danh
│   │   │   ├── Assignments/    # Bài tập
│   │   │   ├── Grading/        # Điểm số
│   │   │   ├── Enrollment/     # Đăng ký học
│   │   │   └── ...             # Các trang khác
│   │   ├── App.jsx             # Router configuration
│   │   └── index.css           # Global styles (dark theme)
│   └── package.json
│
├── infrastructure/
│   ├── db/init.sql             # PostgreSQL init script
│   └── nginx/default.conf      # Nginx reverse proxy config
│
├── scripts/
│   ├── seed_data.py            # Seed dữ liệu mẫu
│   └── gen_password.py         # Tạo hash password
│
├── docker-compose.yml          # PostgreSQL container
└── start.sh                    # Script khởi động tự động
```

---

## Deploy Production

### Render.com

**Backend (Web Service)**:
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  ```
  DATABASE_URL=postgresql://...
  JWT_SECRET_KEY=<your-secure-secret>
  FRONTEND_URL=https://your-frontend.onrender.com
  ENVIRONMENT=production
  ```

**Frontend (Static Site)**:
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Environment Variables:
  ```
  VITE_API_BASE_URL=https://your-backend.onrender.com
  ```

### Docker Compose (Self-hosted)
```bash
# Production với Nginx
docker-compose -f docker-compose.prod.yml up -d
```

---

## ⚙️ Biến môi trường Backend

| Biến | Mô tả | Mặc định |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://ems_admin:ems_password123@localhost:5432/hust_ems` |
| `JWT_SECRET_KEY` | Khóa bí mật JWT | `hust-ems-super-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Thời gian hết hạn token | `60` |
| `FRONTEND_URL` | URL frontend (CORS) | `http://localhost:5173` |
| `ENVIRONMENT` | Môi trường | `development` |

---

## 🔄 Quy trình tạo lớp học

```
1. Admin tạo Môn học  →  /courses
2. Admin tạo Lớp học  →  /classes (gồm: mã lớp, học kỳ, phòng học, lịch học)
3. Admin Gán GV       →  POST /classes/{course_id}/{class_id}/teachers
4. Sinh viên Đăng ký  →  POST /enrollments
5. GV điểm danh       →  POST /attendance
6. GV nhập điểm       →  POST /grading
```

---

## 🐛 Lỗi đã biết & Giải pháp

| Vấn đề | Nguyên nhân | Giải pháp |
|---|---|---|
| Timetable 500 error | `Student.student_id` không tồn tại | Dùng `Student.user_id` |
| Teacher timetable rỗng | Query dùng `teacher_id` thay vì `user_id` | Fix: `Teacher.user_id == current_user.user_id` |
| Route 404 với static path | FastAPI match param route trước | Khai báo static routes trước `/{param}` |
| JWT hết hạn | Token 60 phút | Frontend tự động redirect về login |

---

## 👨‍💻 Phát triển

```bash
# Chạy backend với hot-reload
uvicorn app.main:app --reload --port 8000

# Chạy frontend với hot-reload
npm run dev

# Xem API documentation
open http://localhost:8000/docs

# Reset database
docker-compose down -v && docker-compose up -d
```

---

## 📄 License

MIT License — Free to use for educational purposes.

---

*Được xây dựng cho dự án môn học tại Đại học Bách khoa Hà Nội (HUST)*