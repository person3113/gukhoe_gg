# app/db/database.py 파일 수정
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from app.config import settings

# 데이터베이스 URL에서 메모리 모드인지 확인
is_memory_db = settings.DATABASE_URL == "sqlite:///:memory:"

# connect_args 설정 - SQLite에서만 필요
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# 데이터베이스 엔진 생성 - connect_args 추가
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args
)

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