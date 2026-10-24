from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy import Column, Integer, String
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String)

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, index=True)
    title = Column(String)
    file_url = Column(String) # هنا سنحفظ رابط جوجل درايف
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, index=True)
    q_text = Column(String)
    a_text = Column(String, nullable=True) # الإجابة يمكن أن تكون فارغة في البداية
    votes = Column(Integer, default=0)
