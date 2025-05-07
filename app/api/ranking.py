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

# 활동랭킹 - 참여
@router.get("/ranking/participation")
async def participation_ranking(request: Request, db: Session = Depends(get_db)):
    """
    참여 랭킹 페이지
    """
    # 참여 점수 기준 데이터 조회
    top_legislators = ranking_service.get_top_legislators(db, count=5, category='participation')
    bottom_legislators = ranking_service.get_bottom_legislators(db, count=5, category='participation')
    all_legislators = ranking_service.get_legislators_by_filter(db, category='participation')
    
    # 차트 데이터 생성 (generate_ranking_chart_data 함수는 그대로 사용)
    chart_data = chart_service.generate_ranking_chart_data(top_legislators, bottom_legislators)
    
    # 차트 레이블 수정
    chart_data["top"]["datasets"][0]["label"] = "참여 점수"
    chart_data["bottom"]["datasets"][0]["label"] = "참여 점수"
    
    # 필터 옵션 조회 (종합 페이지와 동일한 방식)
    parties = db.query(Legislator.poly_nm).distinct().all()
    party_list = [party[0] for party in parties]
    
    committees = db.query(Legislator.cmit_nm).distinct().all()
    committee_list = [committee[0] for committee in committees]
    
    terms = db.query(Legislator.reele_gbn_nm).distinct().all()
    term_list = [term[0] for term in terms]
    
    return templates.TemplateResponse(
        "ranking/participation.html", 
        {
            "request": request, 
            "top_legislators": top_legislators,
            "bottom_legislators": bottom_legislators,
            "all_legislators": all_legislators,
            "chart_data": chart_data,
            "category": "participation",
            "filter_options": {
                "parties": party_list,
                "committees": committee_list,
                "terms": term_list
            },
            "current_filters": {}
        }
    )


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