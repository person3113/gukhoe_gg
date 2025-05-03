from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(settings.DATABASE_URL)

# 세션 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

def get_db():
    # DB 세션 생성
    db = SessionLocal()
    try:
        # 세션 반환
        yield db
    finally:
        # 사용 후 세션 닫기 처리
        db.close()