import os
import requests
import time
import random
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import sys
import json

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
    
    # 진행 상황 저장 파일 경로
    progress_file = os.path.join("scripts", "download_progress.json")
    
    # 이미 다운로드한 이미지 목록 불러오기
    downloaded_mona_cds = []
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                downloaded_mona_cds = json.load(f)
            print(f"진행 상황 파일에서 {len(downloaded_mona_cds)}개의 이미 다운로드된 항목을 불러왔습니다.")
        except:
            print("진행 상황 파일을 읽는 중 오류가 발생했습니다. 새로 시작합니다.")
    
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
            
            # 이미 다운로드한 항목이면 건너뛰기
            if legislator.mona_cd in downloaded_mona_cds:
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진은 이전 실행에서 이미 처리되었습니다.")
                success_count += 1
                continue
            
            if os.path.exists(file_path):
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진이 이미 존재합니다. ({local_path})")
                
                # DB에 로컬 경로 업데이트
                if legislator.profile_image_url != local_path:
                    legislator.profile_image_url = local_path
                    db.commit()
                
                # 진행 상황 업데이트
                downloaded_mona_cds.append(legislator.mona_cd)
                with open(progress_file, 'w') as f:
                    json.dump(downloaded_mona_cds, f)
                
                success_count += 1
                continue
            
            # 외부 URL이 없거나 기본 이미지인 경우 건너뛰기
            if not legislator.profile_image_url or legislator.profile_image_url == "/static/images/legislators/default.png":
                print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 URL이 없거나 기본 이미지입니다.")
                
                # 진행 상황 업데이트 (처리 완료로 표시)
                downloaded_mona_cds.append(legislator.mona_cd)
                with open(progress_file, 'w') as f:
                    json.dump(downloaded_mona_cds, f)
                
                continue
            
            # 외부 URL에서 이미지 다운로드 (최대 3번 재시도)
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    if retry_count > 0:
                        print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 재시도 ({retry_count}/{max_retries})...")
                    else:
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
                    
                    # 타임아웃 시간 증가 (연결 타임아웃, 읽기 타임아웃)
                    response = requests.get(image_url, headers=headers, timeout=(30, 60))
                    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
                    
                    # 이미지 저장
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # DB에 로컬 경로 업데이트
                    legislator.profile_image_url = local_path
                    db.commit()
                    
                    print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 완료")
                    success = True
                    success_count += 1
                    
                    # 진행 상황 업데이트
                    downloaded_mona_cds.append(legislator.mona_cd)
                    with open(progress_file, 'w') as f:
                        json.dump(downloaded_mona_cds, f)
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 실패 (최대 재시도 횟수 초과): {str(e)}")
                    else:
                        print(f"[{idx+1}/{total}] {legislator.hg_nm} 의원 사진 다운로드 실패: {str(e)}")
                        # 재시도 전 대기 시간 랜덤화 (1~5초)
                        wait_time = 1 + random.random() * 4
                        print(f"    {wait_time:.1f}초 후 재시도합니다...")
                        time.sleep(wait_time)
            
            # 요청 사이의 대기 시간 증가 (2~4초)
            wait_time = 2 + random.random() * 2
            print(f"다음 요청까지 {wait_time:.1f}초 대기 중...")
            time.sleep(wait_time)
        
        print(f"\n총 {total}명 중 {success_count}명의 의원 사진 다운로드 완료")
    
    finally:
        db.close()

if __name__ == "__main__":
    download_images() 