import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base

def init_db():
    """
    데이터베이스 초기화 - 테이블 생성
    """
    # 모든 모델의 테이블을 생성
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

if __name__ == "__main__":
    init_db()