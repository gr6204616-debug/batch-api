from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# الرابط الخاص بك مع التعديل اللازم لمكتبة SQLAlchemy
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_ZvfJWjaGh9N3@ep-long-morning-b47cw6qm-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
