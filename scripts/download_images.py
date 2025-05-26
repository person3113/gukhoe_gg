import os
import requests
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import sys

# 프로젝트 루트 경로를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.legislator import Legislator
from app.config import settings

# 모든 모델을 명시적으로 임포트
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def download_images():
    """의원 사진을 다운로드하여 로컬에 저장하는 함수"""
    
    # SQLAlchemy 엔진 및 세션 생성
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # 이미지 저장 디렉토리 경로
    save_dir = os.path.join("app", "static", "images", "legislators")
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        # 모든 의원 정보 조회
        legislators = db.query(Legislator).all()
        total = len(legislators)
        print(f"총 {total}명의 의원 사진을 다운로드합니다.")
        
        success_count = 0
        
        for idx, legislator in enumerate(legislators):
            # 파일명은 국회의원 코드 사용 (고유성 보장)
            file_name = f"{legislator.mona_cd}.jpg"
            local_path = f"/static/images/legislators/{file_name}"
            file_path = os.path.join("app", "static", "images", "legislators", file_name)
            
            if os.path.exists(file_path):
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진이 이미 존재합니다. ({local_path})")
                
                # DB에 로컬 경로 업데이트
                if legislator.profile_image_url != local_path:
                    legislator.profile_image_url = local_path
                    db.commit()
                
                success_count += 1
                continue
            
            # 외부 URL이 없거나 기본 이미지인 경우 건너뛰기
            if not legislator.profile_image_url or legislator.profile_image_url == "/static/images/legislators/default.png":
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 URL이 없거나 기본 이미지입니다.")
                continue
            
            # 외부 URL에서 이미지 다운로드
            try:
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 중... ({legislator.profile_image_url})")
                
                # URL이 http:// 또는 https://로 시작하는지 확인
                image_url = legislator.profile_image_url
                if not image_url.startswith(('http://', 'https://')):
                    image_url = f"https:{image_url}" if image_url.startswith('//') else f"http://{image_url}"
                
                # 브라우저처럼 동작하도록 헤더 추가
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': 'https://www.assembly.go.kr/',
                    'sec-ch-ua': '"Google Chrome";v="91", " Not;A Brand";v="99", "Chromium";v="91"',
                    'sec-ch-ua-mobile': '?0',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                
                response = requests.get(image_url, headers=headers, timeout=10)
                response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
                
                # 이미지 저장
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # DB에 로컬 경로 업데이트
                legislator.profile_image_url = local_path
                db.commit()
                
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 완료")
                success_count += 1
                
                # 너무 빠른 요청으로 인한 서버 부하 방지를 위한 딜레이
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 실패: {str(e)}")
        
        print(f"\n총 {total}명 중 {success_count}명의 의원 사진 다운로드 완료")
    
    finally:
        db.close()

if __name__ == "__main__":
    download_images() 