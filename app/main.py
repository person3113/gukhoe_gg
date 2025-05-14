from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from app.models.speech import SpeechByMeeting
from app.db.database import SessionLocal, engine, Base, get_db
from app.api import home, search, champions, ranking, misc_ranking
from app.models.legislator import Legislator

# 모든 모델을 명시적으로 임포트
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def create_app():
    # FastAPI 앱 객체 생성
    app = FastAPI(title="국회.gg", description="국회의원 활동 대시보드")
    
    # 라우터, 정적 파일, 템플릿 설정
    setup_routes(app)
    setup_static(app)
    setup_templates(app)
    
    return app

def setup_routes(app):
    # 각 라우터를 앱에 등록
    app.include_router(home.router)
    app.include_router(search.router)
    app.include_router(champions.router)
    app.include_router(ranking.router)
    app.include_router(misc_ranking.router)
    pass

def setup_static(app):
    # 정적 파일 디렉토리 설정
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    pass

def setup_templates(app):
    # Jinja2 템플릿 엔진 설정
    pass

def init_db():
    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)
    pass

app = create_app()

@app.on_event("startup")
async def startup_event():
    # 애플리케이션 시작 시 실행할 작업
    init_db()
    
    # DB_MODE 환경변수에 따라 데이터 초기화 방법 결정
    db_mode = os.getenv("DB_MODE", "persistent")  # 기본값을 "persistent"로 설정
    
    # DB 세션 생성
    db = SessionLocal()
    try:
        # 기존 데이터 체크
        existing_data = db.query(Legislator).first()
        
        if db_mode == "memory":
            # 메모리 DB 모드일 때만 더미 데이터 생성
            from scripts.create_dummy_data import create_dummy_data
            create_dummy_data()
        elif db_mode == "real_test" or (db_mode == "persistent" and not existing_data):
            # real_test 모드이거나, persistent 모드이면서 데이터가 없는 경우에만 API 호출
            from scripts.fetch_data import fetch_all_data
            fetch_all_data()

        # 데이터 확인 - SpeechByMeeting 데이터가 있는지 확인
        speech_data_count = db.query(SpeechByMeeting).count()
        print(f"회의별 발언 데이터: {speech_data_count}개")
        
        # 데이터가 없는 경우 엑셀 파일 파싱 실행
        if speech_data_count == 0:
            print("회의별 발언 데이터가 없습니다. 엑셀 파일 파싱을 시작합니다...")
            from app.utils.excel_parser import parse_speech_by_meeting_excel
            from app.services.data_processing import process_speech_data
            
            try:
                # 엑셀 파일 파싱
                speech_data = parse_speech_by_meeting_excel()
                # 데이터 처리 및 DB 저장
                process_speech_data(speech_data, db)
                db.commit()
                
                # 저장 후 데이터 확인
                new_speech_data_count = db.query(SpeechByMeeting).count()
                print(f"엑셀 파싱 후 회의별 발언 데이터: {new_speech_data_count}개")
                
                # 샘플 데이터 출력
                sample_data = db.query(SpeechByMeeting).limit(3).all()
                for data in sample_data:
                    print(f"의원ID: {data.legislator_id}, 회의구분: {data.meeting_type}, 횟수: {data.count}")
            except Exception as e:
                print(f"엑셀 파싱 중 오류 발생: {e}")
                db.rollback()  # 오류 발생 시 롤백
    except Exception as e:
        print(f"시작 이벤트 처리 중 오류 발생: {e}")
    finally:
        db.close()