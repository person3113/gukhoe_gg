import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_fetch_excel_data():
    """
    fetch_excel_data 함수만 테스트하는 스크립트
    """
    print("===== 테스트 스크립트 시작 =====")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    
    try:
        print("데이터베이스 연결 시도 중...")
        from app.db.database import SessionLocal
        db = SessionLocal()
        print("데이터베이스 연결 성공!")
        
        print("fetch_excel_data 함수 가져오는 중...")
        from scripts.fetch_data import fetch_excel_data
        
        print("fetch_excel_data 함수 실행 시작...")
        fetch_excel_data(db)
        print("fetch_excel_data 함수 실행 완료!")
        
        db.close()
        print("데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("===== 테스트 스크립트 종료 =====")

if __name__ == "__main__":
    test_fetch_excel_data()