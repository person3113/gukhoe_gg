from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.db.database import engine, Base, get_db
from app.api import home, search, champions, ranking, misc_ranking

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
    db_mode = os.getenv("DB_MODE")
    if db_mode == "memory":
        # 더미 데이터를 사용하는 경우
        from scripts.create_dummy_data import create_dummy_data
        create_dummy_data()
    elif db_mode == "real_test":
        # 실제 데이터를 메모리 DB에 로드하는 경우
        from scripts.fetch_data import fetch_all_data
        fetch_all_data()
    
    # API 키와 기타 설정 로드
    # 필요시 백그라운드 작업 시작
    pass