"""
services/curriculum_service.py — Business logic cho Curriculum management
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.curriculum import Curriculum, CurriculumCourse
from app.models.course import Course


class CurriculumService:

    @staticmethod
    def list_curricula(db: Session) -> list[Curriculum]:
        return db.query(Curriculum).all()

    @staticmethod
    def create_curriculum(db: Session, program_id: str, program_name: str) -> Curriculum:
        if db.query(Curriculum).filter(Curriculum.program_id == program_id).first():
            raise HTTPException(status_code=400, detail=f"ProgramID '{program_id}' đã tồn tại")
        program = Curriculum(program_id=program_id, program_name=program_name)
        db.add(program)
        db.commit()
        db.refresh(program)
        return program

    @staticmethod
    def get_curriculum(db: Session, program_id: str) -> Curriculum:
        program = (
            db.query(Curriculum)
            .options(joinedload(Curriculum.curriculum_courses).joinedload(CurriculumCourse.course))
            .filter(Curriculum.program_id == program_id)
            .first()
        )
        if not program:
            raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
        return program

    @staticmethod
    def update_curriculum(db: Session, program_id: str, program_name: str | None = None) -> Curriculum:
        program = db.query(Curriculum).filter(Curriculum.program_id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
        if program_name:
            program.program_name = program_name
        db.commit()
        db.refresh(program)
        return program

    @staticmethod
    def delete_curriculum(db: Session, program_id: str) -> None:
        program = db.query(Curriculum).filter(Curriculum.program_id == program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
        db.delete(program)
        db.commit()

    @staticmethod
    def add_course(db: Session, program_id: str, course_id: str) -> CurriculumCourse:
        if not db.query(Curriculum).filter(Curriculum.program_id == program_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy chương trình đào tạo")
        if not db.query(Course).filter(Course.course_id == course_id).first():
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        if db.query(CurriculumCourse).filter(
            CurriculumCourse.program_id == program_id,
            CurriculumCourse.course_id == course_id
        ).first():
            raise HTTPException(status_code=400, detail="Môn học đã có trong chương trình này rồi")

        cc = CurriculumCourse(program_id=program_id, course_id=course_id)
        db.add(cc)
        db.commit()
        db.refresh(cc)
        return cc

    @staticmethod
    def remove_course(db: Session, program_id: str, course_id: str) -> None:
        cc = db.query(CurriculumCourse).filter(
            CurriculumCourse.program_id == program_id,
            CurriculumCourse.course_id == course_id
        ).first()
        if not cc:
            raise HTTPException(status_code=404, detail="Môn học không có trong chương trình này")
        db.delete(cc)
        db.commit()
