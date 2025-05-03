import sys
import os
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.services.api_service import ApiService
from app.utils.excel_parser import parse_attendance_excel, parse_speech_keywords_excel, parse_speech_by_meeting_excel
from app.services.data_processing import process_attendance_data, process_speech_data, process_bill_data, process_vote_data

def fetch_all_data():
    """
    모든 데이터 수집 함수 호출
    """
    # DB 세션 생성
    db = SessionLocal()
    try:
        print("Fetching all data...")
        fetch_legislators(db)
        fetch_bills(db)
        fetch_votes(db)
        fetch_committees(db)
        fetch_excel_data(db)
        print("Data fetching completed.")
    finally:
        db.close()

def fetch_legislators(db: Session):
    """
    국회의원 정보 및 SNS 정보 수집
    """
    # ApiService 인스턴스 생성
    api_service = ApiService()
    
    # 호출: api_service.fetch_legislators_info()로 의원 정보 수집
    # 호출: api_service.fetch_legislators_sns()로 의원 SNS 정보 수집
    # DB에 저장
    pass

def fetch_bills(db: Session):
    """
    법안 정보 수집
    """
    # ApiService 인스턴스 생성
    api_service = ApiService()
    
    # 호출: api_service.fetch_bills()로 법안 정보 수집
    # 호출: process_bill_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_votes(db: Session):
    """
    표결 정보 수집
    """
    # ApiService 인스턴스 생성
    api_service = ApiService()
    
    # 호출: api_service.fetch_vote_results()로 표결 정보 수집
    # 호출: process_vote_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_committees(db: Session):
    """
    위원회 정보 수집
    """
    # ApiService 인스턴스 생성
    api_service = ApiService()
    
    # 호출: api_service.fetch_committee_members()로 위원회 정보 수집
    # DB에 저장
    pass

def fetch_excel_data(db: Session):
    """
    엑셀 파일에서 데이터 수집
    """
    # 호출: excel_parser.parse_attendance_excel()로 출석 데이터 수집
    # 호출: excel_parser.parse_speech_keywords_excel()로 발언 키워드 데이터 수집
    # 호출: excel_parser.parse_speech_by_meeting_excel()로 회의별 발언 데이터 수집
    # 호출: process_attendance_data(), process_speech_data()로 데이터 처리
    # DB에 저장
    pass

if __name__ == "__main__":
    fetch_all_data()