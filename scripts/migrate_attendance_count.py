import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine
from sqlalchemy import text

def add_count_column():
    """attendance 테이블에 count 컬럼 추가"""
    try:
        with engine.connect() as conn:
            # 기존 테이블에 count 컬럼이 있는지 확인
            result = conn.execute(text("PRAGMA table_info(attendance)"))
            columns = [row[1] for row in result]
            
            if 'count' not in columns:
                print("attendance 테이블에 count 컬럼 추가 중...")
                conn.execute(text("ALTER TABLE attendance ADD COLUMN count INTEGER DEFAULT 0"))
                conn.commit()
                print("count 컬럼 추가 완료")
            else:
                print("count 컬럼이 이미 존재합니다.")
                
    except Exception as e:
        print(f"마이그레이션 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_count_column()