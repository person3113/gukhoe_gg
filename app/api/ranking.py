from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.services import ranking_service, chart_service
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeMember
from app.services import legislator_service


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/ranking")
async def ranking_home(
    request: Request, 
    db: Session = Depends(get_db),
    party: Optional[str] = None,
    committee: Optional[str] = None,
    term: Optional[str] = None,
    gender: Optional[str] = None
):
    # 필터 옵션 가져오기
    filter_options = legislator_service.get_filter_options(db)
    
    # 현재 적용된 필터 저장
    current_filters = {
        "party": party,
        "committee": committee,
        "term": term,
        "gender": gender
    }
    
    # 종합 점수 기준 상위 5명 조회 (필터 미적용)
    top_legislators = ranking_service.get_top_legislators(db, count=5, category='overall')
    
    # 종합 점수 기준 하위 5명 조회 (필터 미적용)
    bottom_legislators = ranking_service.get_bottom_legislators(db, count=5, category='overall')
    
    # 전체 의원 랭킹 조회 (필터 적용)
    all_legislators = ranking_service.get_legislators_by_filter(
        db, 
        category='overall',
        party=party,
        committee=committee,
        term=term,
        gender=gender
    )
    
    # 현재 카테고리 점수 추가 (표시용)
    for legislator in top_legislators:
        legislator["current_score"] = legislator["overall_score"]
    
    for legislator in bottom_legislators:
        legislator["current_score"] = legislator["overall_score"]
    
    # 차트 데이터 생성
    chart_data = chart_service.generate_ranking_chart_data(top_legislators, bottom_legislators, category='overall')
    
    # 카테고리별 템플릿 정보
    category_info = {
        "overall": {"title": "종합", "score_field": "overall_score"},
        "participation": {"title": "참여", "score_field": "participation_score"},
        "legislation": {"title": "입법활동", "score_field": "legislation_score"},
        "speech": {"title": "의정발언", "score_field": "speech_score"},
        "voting": {"title": "표결 책임성", "score_field": "voting_score"},
        "cooperation": {"title": "협치/초당적 활동", "score_field": "cooperation_score"}
    }
    
    context = {
        "request": request, 
        "top_legislators": top_legislators,
        "bottom_legislators": bottom_legislators,
        "all_legislators": all_legislators,
        "chart_data": chart_data,
        "current_category": "overall",
        "category_info": category_info,
        "title": category_info["overall"]["title"],
        "score_field": category_info["overall"]["score_field"],
        "parties": filter_options["parties"],
        "committees": filter_options["committees"],
        "terms": filter_options["terms"],
        "current_filters": current_filters
    }
    
    return templates.TemplateResponse("ranking/index.html", context)

@router.get("/ranking/{category}")
async def category_ranking(
    request: Request, 
    category: str, 
    db: Session = Depends(get_db),
    party: Optional[str] = None,
    committee: Optional[str] = None,
    term: Optional[str] = None,
    gender: Optional[str] = None
):
    # 카테고리 유효성 검사
    valid_categories = ["overall", "participation", "legislation", "speech", "voting", "cooperation"]
    if category not in valid_categories:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 필터 옵션 가져오기
    filter_options = legislator_service.get_filter_options(db)
    
    # 현재 적용된 필터 저장
    current_filters = {
        "party": party,
        "committee": committee,
        "term": term,
        "gender": gender
    }
    
    # 해당 카테고리 기준 상위 5명 조회 (필터 미적용)
    top_legislators = ranking_service.get_top_legislators(db, count=5, category=category)
    
    # 해당 카테고리 기준 하위 5명 조회 (필터 미적용)
    bottom_legislators = ranking_service.get_bottom_legislators(db, count=5, category=category)
    
    # 전체 의원 랭킹 조회 (필터 적용)
    all_legislators = ranking_service.get_legislators_by_filter(
        db, 
        category=category,
        party=party,
        committee=committee,
        term=term,
        gender=gender
    )
    
    # 카테고리별 템플릿 정보
    category_info = {
        "overall": {"title": "종합", "score_field": "overall_score"},
        "participation": {"title": "참여도", "score_field": "participation_score"},
        "legislation": {"title": "입법활동", "score_field": "legislation_score"},
        "speech": {"title": "의정발언", "score_field": "speech_score"},
        "voting": {"title": "표결 책임성", "score_field": "voting_score"},
        "cooperation": {"title": "정당 간 협력", "score_field": "cooperation_score"}
    }
    
    # 현재 카테고리 점수 추가 (표시용)
    score_field = category_info[category]["score_field"]
    for legislator in top_legislators:
        legislator["current_score"] = legislator[score_field]
    
    for legislator in bottom_legislators:
        legislator["current_score"] = legislator[score_field]
    
    # 차트 데이터 생성
    chart_data = chart_service.generate_ranking_chart_data(top_legislators, bottom_legislators, category=category)
    
    return templates.TemplateResponse(
        "ranking/index.html", 
        {
            "request": request, 
            "top_legislators": top_legislators,
            "bottom_legislators": bottom_legislators,
            "all_legislators": all_legislators,
            "chart_data": chart_data,
            "current_category": category,
            "category_info": category_info,
            "title": category_info[category]["title"],
            "score_field": category_info[category]["score_field"],
            "parties": filter_options["parties"],
            "committees": filter_options["committees"],
            "terms": filter_options["terms"],
            "current_filters": current_filters
        }
    )

@router.get("/api/ranking/{category}")
async def filter_ranking(
    category: str, 
    request: Request, 
    db: Session = Depends(get_db),
    party: Optional[str] = None,
    committee: Optional[str] = None,
    term: Optional[str] = None,
    gender: Optional[str] = None
):
    # 카테고리 유효성 검사
    valid_categories = ["overall", "participation", "legislation", "speech", "voting", "cooperation"]
    if category not in valid_categories:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 필터 적용하여 의원 목록 조회
    legislators = ranking_service.get_legislators_by_filter(
        db, 
        category=category,
        party=party,
        committee=committee,
        term=term,
        gender=gender
    )
    
    # JSON 응답 반환
    return legislators