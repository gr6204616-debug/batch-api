from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# لاحظ التعديلات: إضافة +psycopg2، إزالة الأقواس []، وتشفير الرموز @ # $
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres.ucvtyvuhkerjgzeupexd:3a415c67%40%23%24@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
# إعداد محرك الاتصال بقاعدة بيانات PostgreSQL السحابية
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()