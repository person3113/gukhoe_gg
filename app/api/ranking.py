from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.services import ranking_service, chart_service
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeMember

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/ranking")
async def ranking_home(request: Request, db: Session = Depends(get_db)):
    # 호출: ranking_service.get_top_legislators(category='overall')로 상위 의원 조회
    # 호출: ranking_service.get_bottom_legislators(category='overall')로 하위 의원 조회
    # 호출: ranking_service.get_legislators_by_filter(category='overall')로 전체 의원 랭킹 조회
    # 호출: chart_service.generate_ranking_chart_data()로 차트 데이터 생성
    # 반환: 템플릿 렌더링(ranking/index.html)
    """
    활동 랭킹 홈 페이지
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
    
    Returns:
        템플릿 렌더링(ranking/index.html)
    """
    # 종합 랭킹 기준 상위 5명 의원 조회
    top_legislators = ranking_service.get_top_legislators(db, count=5, category='overall')
    
    # 종합 랭킹 기준 하위 5명 의원 조회
    bottom_legislators = ranking_service.get_bottom_legislators(db, count=5, category='overall')
    
    # 전체 의원 랭킹 조회 (기본 카테고리: overall)
    all_legislators = ranking_service.get_legislators_by_filter(db, category='overall')
    
    # 랭킹 차트 데이터 생성
    chart_data = chart_service.generate_ranking_chart_data(top_legislators, bottom_legislators)
    
    # 템플릿에 전달할 context 생성
    context = {
        "request": request,
        "top_legislators": top_legislators,
        "bottom_legislators": bottom_legislators,
        "all_legislators": all_legislators,
        "chart_data": chart_data,
        "current_category": "overall"
    }
    
    # 템플릿 렌더링
    return templates.TemplateResponse("ranking/index.html", context)

@router.get("/ranking/{category}")
async def category_ranking(request: Request, db: Session = Depends(get_db), category: str = "overall"):
    # 카테고리 유효성 검사 ('participation', 'legislation', 'speech', 'voting', 'cooperation')
    valid_categories = ["overall", "participation", "legislation", "speech", "voting", "cooperation"]
    if category not in valid_categories:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 호출: ranking_service.get_top_legislators(category=category)로 상위 의원 조회
    # 호출: ranking_service.get_bottom_legislators(category=category)로 하위 의원 조회
    # 호출: ranking_service.get_legislators_by_filter(category=category)로 전체 의원 랭킹 조회
    # 호출: chart_service.generate_ranking_chart_data()로 차트 데이터 생성
    # 반환: 템플릿 렌더링(ranking/category.html)
    pass