import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base
from app.main import init_db

def reset_db():
    """
    데이터베이스 초기화 - 모든 테이블 삭제 후 재생성
    """
    print("데이터베이스를 초기화합니다...")
    
    # 모든 테이블 삭제
    Base.metadata.drop_all(bind=engine)
    print("모든 테이블이 삭제되었습니다.")
    
    # 모든 테이블 재생성
    Base.metadata.create_all(bind=engine)
    print("테이블이 재생성되었습니다.")
    
    print("데이터베이스 초기화가 완료되었습니다.")

if __name__ == "__main__":
    # 확인 메시지 출력
    confirm = input("모든 데이터가 삭제됩니다. 계속하시겠습니까? (y/n): ")
    
    if confirm.lower() == 'y':
        reset_db()
    else:
        print("작업이 취소되었습니다.")
