from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from app.core.database import get_db
from app.models.student import Student
from app.models.course import Course
from app.models.exam import Exam
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.course import CourseCreate, CourseResponse
from app.schemas.exam import ExamCreate, ExamResponse

router = APIRouter()

# 基础CRUD端点示例
@router.get("/students", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/courses", response_model=List[CourseResponse])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/exams", response_model=List[ExamResponse])
def get_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exams = db.query(Exam).offset(skip).limit(limit).all()
    return exams

@router.post("/exams", response_model=ExamResponse)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    db_exam = Exam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

# 文件上传端点
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return {"filename": file.filename, "data": df.to_dict(orient="records")}

@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="仅支持Excel文件")

    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    return {"filename": file.filename, "data": df.to_dict(orient="records")}