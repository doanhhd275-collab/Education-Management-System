"""
Script tạo dữ liệu mẫu ban đầu cho database.
Chạy sau khi backend đã start (tables đã được tạo):
    cd backend
    source ../venv/bin/activate
    python ../scripts/seed_data.py
"""
import sys
import os

# Thêm backend vào PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import (
    User, Role, UserRole,
    Student, Teacher, Curriculum, Course,
    CurriculumCourse, CoursePrerequisite, Class, TeacherClass,
    Enrollment, Document
)


def seed():
    # Import engine, Base và tất cả models
    from app.core.database import engine, Base
    import app.models  # noqa - để SQLAlchemy nhận diện models

    print("🗑️  Xóa tables cũ (nếu có schema lỗi)...")
    Base.metadata.drop_all(bind=engine)
    print("📦 Tạo lại tables với schema mới...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tables sẵn sàng")

    db = SessionLocal()
    try:
        print("🌱 Bắt đầu seed dữ liệu...")


        # ── 1. Roles ──────────────────────────────────────────
        roles_data = [
            ("ADMIN",   "Quản trị viên"),
            ("TEACHER", "Giáo viên"),
            ("STUDENT", "Sinh viên"),
        ]
        for role_id, role_name in roles_data:
            if not db.get(Role, role_id):
                db.add(Role(role_id=role_id, role_name=role_name))
        db.commit()
        print("  ✓ Roles")

        # ── 2. Users ──────────────────────────────────────────
        hashed_pw = hash_password("Admin@123")
        users_data = [
            ("U001", "admin@ems.edu.vn",    "Nguyễn Quản Trị",  "0901234567"),
            ("U002", "teacher1@ems.edu.vn", "Trần Văn Giáo",    "0902345678"),
            ("U003", "teacher2@ems.edu.vn", "Lê Thị Hương",     "0903456789"),
            ("U004", "student1@ems.edu.vn", "Phạm Văn An",      "0904567890"),
            ("U005", "student2@ems.edu.vn", "Nguyễn Thị Bình",  "0905678901"),
            ("U006", "student3@ems.edu.vn", "Hoàng Văn Cường",  "0906789012"),
            ("U007", "student4@ems.edu.vn", "Trịnh Thị Dung",   "0907890123"),
        ]
        for user_id, email, name, contact in users_data:
            if not db.get(User, user_id):
                db.add(User(
                    user_id=user_id, email=email,
                    password=hashed_pw, name=name, contact=contact
                ))
        db.commit()
        print("  ✓ Users")

        # ── 3. User Roles ─────────────────────────────────────
        role_assignments = [
            ("U001", "ADMIN"),
            ("U002", "TEACHER"),
            ("U003", "TEACHER"),
            ("U004", "STUDENT"),
            ("U005", "STUDENT"),
            ("U006", "STUDENT"),
            ("U007", "STUDENT"),
        ]
        for user_id, role_id in role_assignments:
            existing = db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            ).first()
            if not existing:
                db.add(UserRole(user_id=user_id, role_id=role_id))
        db.commit()
        print("  ✓ UserRoles")

        # ── 4. Chương trình đào tạo ───────────────────────────
        programs = [
            ("CNTT-K65", "Công nghệ thông tin Khóa 65"),
            ("CNTT-K66", "Công nghệ thông tin Khóa 66"),
            ("DTVT-K65", "Điện tử viễn thông Khóa 65"),
        ]
        for pid, pname in programs:
            if not db.get(Curriculum, pid):
                db.add(Curriculum(program_id=pid, program_name=pname))
        db.commit()
        print("  ✓ Curriculum")

        # ── 5. Sinh viên ──────────────────────────────────────
        students = [
            ("U004", "CNTT-K65", 3.2, 3.2, 0, False),
            ("U005", "CNTT-K65", 2.8, 2.8, 1, False),
            ("U006", "CNTT-K66", 3.5, 3.5, 0, False),
            ("U007", "DTVT-K65", 3.0, 3.0, 0, False),
        ]
        for uid, pid, cpa, gpa, warn, grad in students:
            # PK giờ chỉ là user_id (single key)
            if not db.get(Student, uid):
                db.add(Student(
                    user_id=uid, program_id=pid,
                    cpa=cpa, gpa=gpa,
                    warning_level=warn, graduation_condition=grad
                ))
        db.commit()
        print("  ✓ Students")


        # ── 6. Giáo viên ──────────────────────────────────────
        teachers = [("T001", "U002"), ("T002", "U003")]
        for tid, uid in teachers:
            if not db.get(Teacher, tid):
                db.add(Teacher(teacher_id=tid, user_id=uid))
        db.commit()
        print("  ✓ Teachers")

        # ── 7. Môn học ────────────────────────────────────────
        courses = [
            ("IT3000", "Lập trình căn bản"),
            ("IT3001", "Cấu trúc dữ liệu và giải thuật"),
            ("IT3002", "Cơ sở dữ liệu"),
            ("IT3003", "Phân tích thiết kế hệ thống"),
            ("IT3004", "Lập trình Web"),
            ("IT3005", "Mạng máy tính"),
            ("IT3006", "Trí tuệ nhân tạo"),
        ]
        for cid, cname in courses:
            if not db.get(Course, cid):
                db.add(Course(course_id=cid, course_name=cname))
        db.commit()
        print("  ✓ Courses")

        # ── 8. Môn tiên quyết ─────────────────────────────────
        prereqs = [("IT3001", "IT3000"), ("IT3004", "IT3000"), ("IT3003", "IT3002")]
        for cid, prereq_id in prereqs:
            existing = db.query(CoursePrerequisite).filter(
                CoursePrerequisite.course_id == cid,
                CoursePrerequisite.prerequisite_course_id == prereq_id
            ).first()
            if not existing:
                db.add(CoursePrerequisite(course_id=cid, prerequisite_course_id=prereq_id))
        db.commit()
        print("  ✓ CoursePrerequisites")

        # ── 9. Curriculum Courses ─────────────────────────────
        cc_data = [
            ("CNTT-K65", "IT3000"), ("CNTT-K65", "IT3001"),
            ("CNTT-K65", "IT3002"), ("CNTT-K65", "IT3003"),
            ("CNTT-K65", "IT3004"), ("CNTT-K65", "IT3005"),
            ("CNTT-K66", "IT3000"), ("CNTT-K66", "IT3001"),
            ("CNTT-K66", "IT3002"), ("CNTT-K66", "IT3004"),
            ("CNTT-K66", "IT3006"),
        ]
        for pid, cid in cc_data:
            existing = db.query(CurriculumCourse).filter(
                CurriculumCourse.program_id == pid,
                CurriculumCourse.course_id == cid
            ).first()
            if not existing:
                db.add(CurriculumCourse(program_id=pid, course_id=cid))
        db.commit()
        print("  ✓ CurriculumCourses")

        # ── 10. Lớp học ───────────────────────────────────────
        classes = [
            ("IT3000", "IT3000-01", "2024-1", 40),
            ("IT3000", "IT3000-02", "2024-1", 40),
            ("IT3001", "IT3001-01", "2024-1", 35),
            ("IT3002", "IT3002-01", "2024-1", 40),
            ("IT3003", "IT3003-01", "2024-2", 35),
            ("IT3004", "IT3004-01", "2024-2", 40),
        ]
        for course_id, class_id, semester, cap in classes:
            existing = db.query(Class).filter(
                Class.course_id == course_id,
                Class.class_id == class_id
            ).first()
            if not existing:
                db.add(Class(
                    course_id=course_id, class_id=class_id,
                    semester=semester, capacity=cap
                ))
        db.commit()
        print("  ✓ Classes")

        # ── 11. Phân công giáo viên ───────────────────────────
        tc_data = [
            ("T001", "2024-1", "IT3000-01", "IT3000"),
            ("T001", "2024-1", "IT3001-01", "IT3001"),
            ("T002", "2024-1", "IT3000-02", "IT3000"),
            ("T002", "2024-1", "IT3002-01", "IT3002"),
            ("T001", "2024-2", "IT3003-01", "IT3003"),
            ("T002", "2024-2", "IT3004-01", "IT3004"),
        ]
        for tid, sem, cid, course_id in tc_data:
            existing = db.query(TeacherClass).filter(
                TeacherClass.teacher_id == tid,
                TeacherClass.semester == sem,
                TeacherClass.class_id == cid
            ).first()
            if not existing:
                db.add(TeacherClass(
                    teacher_id=tid, semester=sem,
                    class_id=cid, course_id=course_id
                ))
        db.commit()
        print("  ✓ TeacherClasses")

        # ── 12. Đăng ký học ───────────────────────────────────
        enrollments = [
            ("IT3000-01", "IT3000", "U004", 7.5,  8.0,  "B", "STUDYING"),
            ("IT3000-01", "IT3000", "U005", 6.0,  5.5,  "C", "STUDYING"),
            ("IT3001-01", "IT3001", "U004", 8.0,  8.5,  "A", "STUDYING"),
            ("IT3002-01", "IT3002", "U005", None, None, None, "STUDYING"),
            ("IT3000-02", "IT3000", "U006", 9.0,  9.5,  "A", "PASSED"),
            ("IT3000-01", "IT3000", "U007", 5.5,  6.0,  "C", "STUDYING"),
        ]
        for class_id, course_id, sid, mid, final, grade, status in enrollments:
            existing = db.query(Enrollment).filter(
                Enrollment.class_id == class_id,
                Enrollment.student_id == sid
            ).first()
            if not existing:
                db.add(Enrollment(
                    class_id=class_id, course_id=course_id,
                    student_id=sid, midterm_score=mid,
                    final_term_score=final, grade=grade, status=status
                ))
        db.commit()
        print("  ✓ Enrollments")

        # ── 13. Tài liệu ──────────────────────────────────────
        docs = [
            ("DOC001", "Slide bài giảng Tuần 1 - Lập trình căn bản", "T001"),
            ("DOC002", "Bài tập thực hành Chương 1",                  "T001"),
            ("DOC003", "Slide CTDL - Mảng và Danh sách liên kết",     "T001"),
            ("DOC004", "Tài liệu Cơ sở dữ liệu - SQL cơ bản",        "T002"),
            ("DOC005", "Slide Lập trình Web - HTML/CSS",               "T002"),
        ]
        for did, dname, tid in docs:
            if not db.get(Document, did):
                db.add(Document(document_id=did, document_name=dname, teacher_id=tid))
        db.commit()
        print("  ✓ Documents")

        print()
        print("✅ Seed dữ liệu hoàn tất!")
        print()
        print("Tài khoản test:")
        print("  admin@ems.edu.vn    / Admin@123  (ADMIN)")
        print("  teacher1@ems.edu.vn / Admin@123  (TEACHER)")
        print("  student1@ems.edu.vn / Admin@123  (STUDENT)")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
