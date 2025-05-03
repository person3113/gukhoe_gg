from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services import ranking_service, chart_service

router = APIRouter()

@router.get("/ranking")
async def ranking_home(request: Request, db: Session = Depends(get_db)):
    # 호출: ranking_service.get_top_legislators(category='overall')로 상위 의원 조회
    # 호출: ranking_service.get_bottom_legislators(category='overall')로 하위 의원 조회
    # 호출: ranking_service.get_legislators_by_filter(category='overall')로 전체 의원 랭킹 조회
    # 호출: chart_service.generate_ranking_chart_data()로 차트 데이터 생성
    # 반환: 템플릿 렌더링(ranking/index.html)
    pass

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