from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import os

from app.db.database import get_db
from app.services import ranking_service, chart_service

router = APIRouter()

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # 종합 랭킹 기준 상위 5명 국회의원 조회
    top_legislators = ranking_service.get_top_legislators(db, count=5, category='overall')
    
    # 상위 5명 국회의원 점수 차트 데이터 생성
    chart_data = chart_service.generate_top_score_chart_data(top_legislators)
    
    # 템플릿에 전달할 context 생성
    context = {
        "request": request,
        "top_legislators": top_legislators,
        "chart_data": chart_data
    }
    
    # 템플릿 렌더링하여 응답
    return templates.TemplateResponse("home.html", context)