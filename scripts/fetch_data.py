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
    # 호출: fetch_legislators()
    # 호출: fetch_bills()
    # 호출: fetch_votes()
    # 호출: fetch_committees()
    # 호출: fetch_committee_info()  # 추가
    # 호출: fetch_processed_bills_stats()  # 추가
    # 호출: fetch_excel_data()
    # DB 세션 닫기
    pass

def fetch_legislators(db: Session):
    """
    국회의원 정보, SNS 정보, 사진 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_legislators_info()로 의원 정보 수집
    # 호출: api_service.fetch_legislators_sns()로 의원 SNS 정보 수집
    # 호출: api_service.fetch_legislator_images()로 의원 사진 정보 수집
    # 국회의원코드(mona_cd)를 기준으로 사진 정보 매핑 딕셔너리 생성
    # 의원 정보에 사진 URL 추가 (이미지 없는 경우 기본 이미지 경로 설정)
    # 국회의원 및 SNS 정보 DB에 저장
    pass

def fetch_bills(db: Session):
    """
    법안 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_bills()로 법안 정보 수집
    # 호출: process_bill_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_votes(db: Session):
    """
    표결 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_vote_results()로 표결 정보 수집
    # 호출: process_vote_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_committees(db: Session):
    """
    위원회 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_committee_members()로 위원회 정보 수집
    # DB에 저장
    pass

def fetch_committee_info(db: Session):
    """
    위원회 현황 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_committee_info()로 위원회 현황 정보 수집
    # 위원회 테이블에서 해당 위원회 조회 후 정보 업데이트 또는 새로 생성
    # 변경사항 커밋
    pass

def fetch_processed_bills_stats(db: Session):
    """
    처리 의안통계(위원회별) 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_processed_bills_stats()로 처리 의안통계 수집
    # 위원회 테이블에서 해당 위원회 조회 후 접수건수, 처리건수 정보 업데이트
    # 변경사항 커밋
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