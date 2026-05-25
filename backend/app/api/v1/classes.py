"""
Router: Quản lý lớp học (Classes)
Endpoints:
  GET    /api/v1/classes                                      — Danh sách lớp
  POST   /api/v1/classes                                      — ADMIN: tạo lớp
  GET    /api/v1/classes/{course_id}/{class_id}               — Chi tiết lớp
  PUT    /api/v1/classes/{course_id}/{class_id}               — ADMIN: cập nhật
  DELETE /api/v1/classes/{course_id}/{class_id}               — ADMIN: xóa
  POST   /api/v1/classes/{course_id}/{class_id}/teachers      — ADMIN: gán giáo viên
  GET    /api/v1/classes/{course_id}/{class_id}/students      — Danh sách sinh viên trong lớp
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import Class, TeacherClass, Teacher, Enrollment, Student, User, Course
from app.schemas.class_ import ClassCreate, ClassUpdate, ClassResponse, TeacherClassCreate, TeacherClassResponse

router = APIRouter(prefix="/classes", tags=["Quản lý lớp học"])


@router.get("", response_model=list[ClassResponse])
def list_classes(
    course_id: str | None = Query(None, description="Lọc theo môn học"),
    semester: str | None = Query(None, description="Lọc theo học kỳ"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Lấy danh sách lớp học (có thể lọc theo môn và học kỳ)."""
    query = db.query(Class)

    if course_id:
        query = query.filter(Class.course_id == course_id)
    if semester:
        query = query.filter(Class.semester == semester)

    classes = query.offset((page - 1) * page_size).limit(page_size).all()
    return classes


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Tạo lớp học mới. Chỉ ADMIN."""
    # Kiểm tra môn học tồn tại
    if not db.query(Course).filter(Course.course_id == data.course_id).first():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy môn học '{data.course_id}'")

    # Kiểm tra lớp chưa tồn tại (composite PK: CourseID + ClassID)
    existing = db.query(Class).filter(
        Class.course_id == data.course_id,
        Class.class_id == data.class_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Lớp '{data.class_id}' của môn '{data.course_id}' đã tồn tại"
        )

    new_class = Class(
        course_id=data.course_id,
        class_id=data.class_id,
        semester=data.semester,
        capacity=data.capacity,
        day_of_week=data.day_of_week,
        start_period=data.start_period,
        end_period=data.end_period,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@router.get("/{course_id}/{class_id}", response_model=ClassResponse)
def get_class(
    course_id: str,
    class_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Xem chi tiết lớp học."""
    class_ = db.query(Class).filter(
        Class.course_id == course_id,
        Class.class_id == class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return class_


@router.put("/{course_id}/{class_id}", response_model=ClassResponse)
def update_class(
    course_id: str,
    class_id: str,
    data: ClassUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Cập nhật thông tin lớp học. Chỉ ADMIN."""
    class_ = db.query(Class).filter(
        Class.course_id == course_id,
        Class.class_id == class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(class_, field, value)

    db.commit()
    db.refresh(class_)
    return class_


@router.delete("/{course_id}/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    course_id: str,
    class_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Xóa lớp học. Chỉ ADMIN."""
    class_ = db.query(Class).filter(
        Class.course_id == course_id,
        Class.class_id == class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    db.delete(class_)
    db.commit()


@router.post("/{course_id}/{class_id}/teachers", response_model=TeacherClassResponse, status_code=201)
def assign_teacher(
    course_id: str,
    class_id: str,
    data: TeacherClassCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN"))
):
    """Gán giáo viên dạy lớp. Chỉ ADMIN."""
    # Kiểm tra lớp và giáo viên tồn tại
    class_ = db.query(Class).filter(
        Class.course_id == course_id,
        Class.class_id == class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    if not db.query(Teacher).filter(Teacher.teacher_id == data.teacher_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")

    # Kiểm tra chưa được gán
    existing = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == data.teacher_id,
        TeacherClass.class_id == class_id,
        TeacherClass.semester == data.semester
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Giáo viên đã được gán vào lớp này rồi")

    tc = TeacherClass(
        teacher_id=data.teacher_id,
        semester=data.semester,
        class_id=class_id,
        course_id=course_id
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


@router.get("/{course_id}/{class_id}/students")
def get_class_students(
    course_id: str,
    class_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("ADMIN", "TEACHER"))
):
    """
    Lấy danh sách sinh viên trong lớp kèm điểm số.
    ADMIN và TEACHER được xem.
    """
    class_ = db.query(Class).filter(
        Class.course_id == course_id,
        Class.class_id == class_id
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    enrollments = (
        db.query(Enrollment)
        .options(joinedload(Enrollment.student).joinedload(Student.user))
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.class_id == class_id
        )
        .all()
    )

    result = []
    for e in enrollments:
        student_user = e.student.user if e.student else None
        result.append({
            "student_id":       e.student_id,
            "student_name":     student_user.name if student_user else "N/A",
            "midterm_score":    e.midterm_score,
            "final_term_score": e.final_term_score,
            "grade":            e.grade,
            "status":           e.status,
        })
    return result


# ── Thời khóa biểu ─────────────────────────────────────────────

@router.get("/timetable/teacher", tags=["Thời khóa biểu"])
def teacher_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trả về thời khóa biểu của giáo viên đang đăng nhập.
    Bao gồm lớp + lịch học + tên môn.
    """
    from app.models.user import TeacherClass, Teacher as TeacherModel
    # Tìm teacher_id từ user hiện tại
    teacher = db.query(TeacherModel).filter(TeacherModel.teacher_id == current_user.user_id).first()
    if not teacher:
        return []  # Không phải giáo viên

    tcs = (
        db.query(TeacherClass)
        .options(
            joinedload(TeacherClass.class_).joinedload(Class.course)
        )
        .filter(TeacherClass.teacher_id == teacher.teacher_id)
        .all()
    )

    result = []
    for tc in tcs:
        cls = tc.class_
        if not cls:
            continue
        result.append({
            "class_id":     cls.class_id,
            "course_id":    cls.course_id,
            "course_name":  cls.course.course_name if cls.course else cls.course_id,
            "semester":     cls.semester or tc.semester,
            "capacity":     cls.capacity,
            "day_of_week":  cls.day_of_week,
            "start_period": cls.start_period,
            "end_period":   cls.end_period,
        })
    return result


@router.get("/timetable/student", tags=["Thời khóa biểu"])
def student_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trả về thời khóa biểu của sinh viên đang đăng nhập.
    Bao gồm lớp đã đăng ký + lịch học + tên môn.
    """
    from app.models.user import Student as StudentModel
    student = db.query(StudentModel).filter(StudentModel.student_id == current_user.user_id).first()
    if not student:
        return []

    enrollments_list = (
        db.query(Enrollment)
        .options(
            joinedload(Enrollment.class_).joinedload(Class.course)
        )
        .filter(Enrollment.student_id == student.student_id)
        .all()
    )

    result = []
    for e in enrollments_list:
        cls = e.class_
        if not cls:
            continue
        result.append({
            "class_id":     cls.class_id,
            "course_id":    cls.course_id,
            "course_name":  cls.course.course_name if cls.course else cls.course_id,
            "semester":     cls.semester,
            "capacity":     cls.capacity,
            "day_of_week":  cls.day_of_week,
            "start_period": cls.start_period,
            "end_period":   cls.end_period,
        })
    return result

