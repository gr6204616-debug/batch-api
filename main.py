from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import bcrypt

# استدعاء ملفات قاعدة البيانات
from database import engine, SessionLocal
import models

# 1. إنشاء الجداول في قاعدة البيانات إذا لم تكن موجودة
models.Base.metadata.create_all(bind=engine)

# 2. إعداد التطبيق والمجلدات
app = FastAPI(title="نظام إدارة الدفعة")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 3. إعدادات جدار الحماية (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. دالة الاتصال بقاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. هياكل البيانات (Pydantic Models)
class LoginRequest(BaseModel):
    email: str
    password: str

class Subject(BaseModel):
    id: str
    name: str
    icon: str
    is_new: int

class Homework(BaseModel):
    id: int
    subject_id: str
    title: str
    due_date: str
    is_done: bool

# 6. البيانات الوهمية (المتبقية لحين ربطها بالقاعدة لاحقاً)
db_subjects = [
    {"id": "oop", "name": "برمجة شيئية", "icon": "💻", "is_new": 0},
    {"id": "num", "name": "التحليل العددي", "icon": "✍️", "is_new": 0},
    {"id": "comp", "name": "النظرية الاحتسابية", "icon": "🧮", "is_new": 0},
    {"id": "py", "name": "لغة بايثون", "icon": "🐍", "is_new": 0},
    {"id": "ar", "name": "اللغة العربية", "icon": "📚", "is_new": 0},
    {"id": "alg", "name": "خوارزميات AI", "icon": "🤖", "is_new": 0}
]

db_homeworks = [
    {"id": 1, "subject_id": "oop", "title": "واجب الوراثة", "due_date": "بعد يومين", "is_done": False},
    {"id": 3, "subject_id": "py", "title": "مشروع حاسبة", "due_date": "الأسبوع القادم", "is_done": False}
]

# ==========================================
# 7. المسارات (API Endpoints) - يجب أن تكون منظمة
# ==========================================

# مسار تسجيل الدخول
@app.post("/api/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="الحساب غير موجود")
    
    is_valid = bcrypt.checkpw(credentials.password.encode('utf-8'), user.hashed_password.encode('utf-8'))
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="كلمة المرور خاطئة")
        
    return {
        "status": "success",
        "message": "تم تسجيل الدخول بنجاح",
        "user": {
            "name": user.name,
            "email": user.email,
            "role": user.role 
        }
    }

# مسارات المواد والواجبات
@app.get("/api/subjects", response_model=List[Subject])
def get_subjects():
    return db_subjects

@app.get("/api/homeworks", response_model=List[Homework])
def get_homeworks():
    return db_homeworks

@app.post("/api/homeworks/{hw_id}/toggle")
def toggle_homework(hw_id: int):
    for hw in db_homeworks:
        if hw["id"] == hw_id:
            hw["is_done"] = not hw["is_done"]
            return {"status": "success", "message": f"تم تحديث الواجب {hw_id}", "new_status": hw["is_done"]}
    raise HTTPException(status_code=404, detail="الواجب غير موجود")

# مسارات رفع وعرض المحاضرات
@app.get("/api/lectures/{subject_id}")
def get_lectures(subject_id: str, db: Session = Depends(get_db)):
    lectures = db.query(models.Lecture).filter(models.Lecture.subject_id == subject_id).order_by(models.Lecture.id.desc()).all()
    return lectures

@app.post("/api/lectures/upload")
def upload_lecture(
    subject_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = file.filename.split('.')[-1].upper()
    file_location = f"uploads/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    new_lecture = models.Lecture(
        subject_id=subject_id,
        title=title,
        file_type=ext,
        file_url=f"http://127.0.0.1:8000/{file_location}"
    )
    db.add(new_lecture)
    db.commit()
    
    return {"status": "success", "message": "تم رفع الملف بنجاح"}
# مسار حذف ملف (من قاعدة البيانات ومن مجلد uploads)
@app.delete("/api/lectures/{lecture_id}")
def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    # 1. البحث عن الملف في قاعدة البيانات باستخدام الـ ID
    lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
    
    if not lecture:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    
    # 2. حذف الملف الفعلي من القرص الصلب (مجلد uploads)
    # نستخرج اسم الملف من الرابط
    file_name = lecture.file_url.split("/")[-1]
    file_path = f"uploads/{file_name}"
    
    if os.path.exists(file_path):
        os.remove(file_path) # هذا السطر يمسح الملف من حاسوبك نهائياً
        
    # 3. حذف السجل من قاعدة البيانات
    db.delete(lecture)
    db.commit()
    
    return {"status": "success", "message": "تم الحذف بنجاح"}