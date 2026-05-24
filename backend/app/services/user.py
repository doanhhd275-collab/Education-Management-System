from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user import Course
from app.schemas.user import CourseCreate

def create_course(CourseCreate):
    newcourse
    newcourse.course_id =CourseCreate.course_id
    newcourse.course_name=CourseCreate.course_name