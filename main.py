from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import bcrypt

from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="نظام إدارة الدفعة")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    email: str
    password: str

class LectureCreate(BaseModel):
    subject_id: str
    title: str
    file_url: str

class SubjectResponse(BaseModel):
    id: str
    name: str
    icon: str
    is_new: int

class HomeworkResponse(BaseModel):
    id: int
    subject_id: str
    title: str
    due_date: str
    is_done: bool
class QuestionCreate(BaseModel):
    subject_id: str
    q_text: str

class AnswerCreate(BaseModel):
    a_text: str

@app.get("/api/questions/{subject_id}")
def get_questions(subject_id: str, db: Session = Depends(get_db)):
    # ترتيب الأسئلة حسب التصويت (الأعلى أولاً)
    return db.query(models.Question).filter(models.Question.subject_id == subject_id).order_by(models.Question.votes.desc()).all()

@app.post("/api/questions/add")
def add_question(q: QuestionCreate, db: Session = Depends(get_db)):
    new_q = models.Question(subject_id=q.subject_id, q_text=q.q_text, a_text="")
    db.add(new_q)
    db.commit()
    return {"status": "success"}

@app.post("/api/questions/{q_id}/answer")
def answer_question(q_id: int, ans: AnswerCreate, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == q_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="السؤال غير موجود")
    question.a_text = ans.a_text
    db.commit()
    return {"status": "success"}

@app.post("/api/questions/{q_id}/vote")
def vote_question(q_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == q_id).first()
    if question:
        question.votes += 1
        db.commit()
    return {"status": "success"}
# بيانات وهمية مؤقتة للمواد والواجبات
db_subjects = [
    {"id": "oop", "name": "برمجة شيئية", "icon": "💻", "is_new": 0},
    {"id": "num", "name": "التحليل العددي", "icon": "✍️", "is_new": 0},
    {"id": "comp", "name": "النظرية الاحتسابية", "icon": "🧮", "is_new": 0},
    {"id": "py", "name": "لغة بايثون", "icon": "🐍", "is_new": 0},
    {"id": "ar", "name": "اللغة العربية", "icon": "📚", "is_new": 0},
    {"id": "alg", "name": "خوارزميات AI", "icon": "🤖", "is_new": 0}
]
db_homeworks = []
    

@app.post("/api/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not bcrypt.checkpw(credentials.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="بيانات الدخول خاطئة")
        
    return {
        "status": "success",
        "message": "تم تسجيل الدخول بنجاح",
        "user": {"name": user.name, "email": user.email, "role": user.role}
    }

@app.get("/api/subjects", response_model=List[SubjectResponse])
def get_subjects():
    return db_subjects

@app.get("/api/homeworks", response_model=List[HomeworkResponse])
def get_homeworks():
    return db_homeworks

@app.post("/api/homeworks/{hw_id}/toggle")
def toggle_homework(hw_id: int):
    for hw in db_homeworks:
        if hw["id"] == hw_id:
            hw["is_done"] = not hw["is_done"]
            return {"status": "success", "new_status": hw["is_done"]}
    raise HTTPException(status_code=404, detail="الواجب غير موجود")

@app.get("/api/lectures/{subject_id}")
def get_lectures(subject_id: str, db: Session = Depends(get_db)):
    return db.query(models.Lecture).filter(models.Lecture.subject_id == subject_id).order_by(models.Lecture.id.desc()).all()

@app.post("/api/lectures/add")
def add_lecture(lecture: LectureCreate, db: Session = Depends(get_db)):
    new_lecture = models.Lecture(
        subject_id=lecture.subject_id,
        title=lecture.title,
        file_url=lecture.file_url
    )
    db.add(new_lecture)
    db.commit()
    return {"status": "success", "message": "تمت إضافة الرابط بنجاح"}

@app.delete("/api/lectures/{lecture_id}")
def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    db.delete(lecture)
    db.commit()
    return {"status": "success", "message": "تم الحذف بنجاح"}
@app.delete("/api/questions/{q_id}")
def delete_question(q_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == q_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="السؤال غير موجود")
    db.delete(question)
    db.commit()
    return {"status": "success", "message": "تم الحذف بنجاح"}
