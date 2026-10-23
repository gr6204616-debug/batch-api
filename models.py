from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String) # لن نحفظ الباسورد مكشوفاً أبداً
    role = Column(String, default="student") # student أو admin
    is_active = Column(Boolean, default=True)
class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, index=True)
    title = Column(String)
    file_type = Column(String)
    file_url = Column(String)