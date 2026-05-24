-- =====================================================
-- EMS - Seed Data (Dữ liệu mẫu ban đầu)
-- Chạy file này để có dữ liệu test ngay lập tức
-- =====================================================

-- Lưu ý: Bảng được tạo tự động bởi SQLAlchemy (main.py → Base.metadata.create_all)
-- File này chỉ INSERT dữ liệu mẫu

-- ── 1. Roles ─────────────────────────────────────────────────
INSERT INTO roles ("RoleID", "RoleName") VALUES
    ('ADMIN',   'Quản trị viên'),
    ('TEACHER', 'Giáo viên'),
    ('STUDENT', 'Sinh viên')
ON CONFLICT ("RoleID") DO NOTHING;

-- ── 2. Users ─────────────────────────────────────────────────
-- Mật khẩu: Admin@123 (đã băm bcrypt)
-- Để đổi mật khẩu: dùng Python → bcrypt.hash("mật_khẩu_mới")
INSERT INTO users ("UserID", "Email", "Password", "Name", "Contact") VALUES
    ('U001', 'admin@ems.edu.vn',    '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Nguyễn Quản Trị',    '0901234567'),
    ('U002', 'teacher1@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Trần Văn Giáo',      '0902345678'),
    ('U003', 'teacher2@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Lê Thị Hương',       '0903456789'),
    ('U004', 'student1@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Phạm Văn An',        '0904567890'),
    ('U005', 'student2@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Nguyễn Thị Bình',    '0905678901'),
    ('U006', 'student3@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Hoàng Văn Cường',    '0906789012'),
    ('U007', 'student4@ems.edu.vn', '$2b$12$LQv3c1yqBwEHFi.rYWXVRuBl5hJMz5vjhrgKDumDFUuLT0hLUbp0K', 'Trịnh Thị Dung',     '0907890123')
ON CONFLICT ("UserID") DO NOTHING;

-- ── 3. Gán Roles cho Users ───────────────────────────────────
INSERT INTO user_roles ("UserID", "RoleID") VALUES
    ('U001', 'ADMIN'),
    ('U002', 'TEACHER'),
    ('U003', 'TEACHER'),
    ('U004', 'STUDENT'),
    ('U005', 'STUDENT'),
    ('U006', 'STUDENT'),
    ('U007', 'STUDENT')
ON CONFLICT ("UserID", "RoleID") DO NOTHING;

-- ── 4. Chương trình đào tạo ──────────────────────────────────
INSERT INTO curriculums ("ProgramID", "ProgramName") VALUES
    ('CNTT-K65',  'Công nghệ thông tin Khóa 65'),
    ('CNTT-K66',  'Công nghệ thông tin Khóa 66'),
    ('DTVT-K65',  'Điện tử viễn thông Khóa 65')
ON CONFLICT ("ProgramID") DO NOTHING;

-- ── 5. Sinh viên ─────────────────────────────────────────────
INSERT INTO students ("UserID", "ProgramID", "CPA", "GPA", "WarningLevel", "GraduationCondition") VALUES
    ('U004', 'CNTT-K65', 3.2, 3.2, 0, false),
    ('U005', 'CNTT-K65', 2.8, 2.8, 1, false),
    ('U006', 'CNTT-K66', 3.5, 3.5, 0, false),
    ('U007', 'DTVT-K65', 3.0, 3.0, 0, false)
ON CONFLICT ("UserID", "ProgramID") DO NOTHING;

-- ── 6. Giáo viên ─────────────────────────────────────────────
INSERT INTO teachers ("TeacherID", "UserID") VALUES
    ('T001', 'U002'),
    ('T002', 'U003')
ON CONFLICT ("TeacherID") DO NOTHING;

-- ── 7. Môn học ───────────────────────────────────────────────
INSERT INTO courses ("CourseID", "CourseName") VALUES
    ('IT3000',  'Lập trình căn bản'),
    ('IT3001',  'Cấu trúc dữ liệu và giải thuật'),
    ('IT3002',  'Cơ sở dữ liệu'),
    ('IT3003',  'Phân tích thiết kế hệ thống'),
    ('IT3004',  'Lập trình Web'),
    ('IT3005',  'Mạng máy tính'),
    ('IT3006',  'Trí tuệ nhân tạo')
ON CONFLICT ("CourseID") DO NOTHING;

-- ── 8. Môn tiên quyết ────────────────────────────────────────
-- IT3001 (CTDL) yêu cầu IT3000 (Lập trình căn bản)
-- IT3004 (Web) yêu cầu IT3000 (Lập trình căn bản)
INSERT INTO course_prerequisites ("CourseID", "PrerequisiteCourseID") VALUES
    ('IT3001', 'IT3000'),
    ('IT3004', 'IT3000'),
    ('IT3003', 'IT3002')
ON CONFLICT ("CourseID", "PrerequisiteCourseID") DO NOTHING;

-- ── 9. Môn học trong chương trình đào tạo ───────────────────
INSERT INTO curriculum_courses ("ProgramID", "CourseID") VALUES
    ('CNTT-K65', 'IT3000'), ('CNTT-K65', 'IT3001'),
    ('CNTT-K65', 'IT3002'), ('CNTT-K65', 'IT3003'),
    ('CNTT-K65', 'IT3004'), ('CNTT-K65', 'IT3005'),
    ('CNTT-K66', 'IT3000'), ('CNTT-K66', 'IT3001'),
    ('CNTT-K66', 'IT3002'), ('CNTT-K66', 'IT3004'),
    ('CNTT-K66', 'IT3006')
ON CONFLICT ("ProgramID", "CourseID") DO NOTHING;

-- ── 10. Lớp học ──────────────────────────────────────────────
INSERT INTO classes ("CourseID", "ClassID", "Semester", "Capacity") VALUES
    ('IT3000', 'IT3000-01', '2024-1', 40),
    ('IT3000', 'IT3000-02', '2024-1', 40),
    ('IT3001', 'IT3001-01', '2024-1', 35),
    ('IT3002', 'IT3002-01', '2024-1', 40),
    ('IT3003', 'IT3003-01', '2024-2', 35),
    ('IT3004', 'IT3004-01', '2024-2', 40)
ON CONFLICT ("CourseID", "ClassID") DO NOTHING;

-- ── 11. Phân công giáo viên ──────────────────────────────────
INSERT INTO teacher_classes ("TeacherID", "Semester", "ClassID", "CourseID") VALUES
    ('T001', '2024-1', 'IT3000-01', 'IT3000'),
    ('T001', '2024-1', 'IT3001-01', 'IT3001'),
    ('T002', '2024-1', 'IT3000-02', 'IT3000'),
    ('T002', '2024-1', 'IT3002-01', 'IT3002'),
    ('T001', '2024-2', 'IT3003-01', 'IT3003'),
    ('T002', '2024-2', 'IT3004-01', 'IT3004')
ON CONFLICT ("TeacherID", "Semester", "ClassID") DO NOTHING;

-- ── 12. Đăng ký học ──────────────────────────────────────────
INSERT INTO enrollments ("ClassID", "CourseID", "StudentID", "MidTermScore", "FinalTermScore", "Grade", "Status") VALUES
    ('IT3000-01', 'IT3000', 'U004', 7.5,  8.0,  'B', 'STUDYING'),
    ('IT3000-01', 'IT3000', 'U005', 6.0,  5.5,  'C', 'STUDYING'),
    ('IT3001-01', 'IT3001', 'U004', 8.0,  8.5,  'A', 'STUDYING'),
    ('IT3002-01', 'IT3002', 'U005', NULL, NULL, NULL, 'STUDYING'),
    ('IT3000-02', 'IT3000', 'U006', 9.0,  9.5,  'A', 'PASSED'),
    ('IT3000-01', 'IT3000', 'U007', 5.5,  6.0,  'C', 'STUDYING')
ON CONFLICT ("ClassID", "StudentID") DO NOTHING;

-- ── 13. Tài liệu học tập ─────────────────────────────────────
INSERT INTO documents ("DocumentID", "DocumentName", "TeacherID") VALUES
    ('DOC001', 'Slide bài giảng Tuần 1 - Lập trình căn bản', 'T001'),
    ('DOC002', 'Bài tập thực hành Chương 1',                  'T001'),
    ('DOC003', 'Slide CTDL - Mảng và Danh sách liên kết',     'T001'),
    ('DOC004', 'Tài liệu Cơ sở dữ liệu - SQL cơ bản',        'T002'),
    ('DOC005', 'Slide Lập trình Web - HTML/CSS',               'T002')
ON CONFLICT ("DocumentID") DO NOTHING;

-- ── Thông tin đăng nhập test ─────────────────────────────────
-- Email: admin@ems.edu.vn    | Mật khẩu: Admin@123 | Role: ADMIN
-- Email: teacher1@ems.edu.vn | Mật khẩu: Admin@123 | Role: TEACHER
-- Email: teacher2@ems.edu.vn | Mật khẩu: Admin@123 | Role: TEACHER
-- Email: student1@ems.edu.vn | Mật khẩu: Admin@123 | Role: STUDENT
-- Email: student2@ems.edu.vn | Mật khẩu: Admin@123 | Role: STUDENT
