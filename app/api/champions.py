from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.db.database import get_db
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import CommitteeHistory
from app.services import legislator_service, stats_service, chart_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/champions")
async def list_champions(
    request: Request, 
    db: Session = Depends(get_db), 
    name: Optional[str] = None, 
    party: Optional[str] = None, 
    district: Optional[str] = None, 
    term: Optional[str] = None
):
    # 필터 옵션 가져오기
    filter_options = legislator_service.get_filter_options(db)
    
    # 필터링된 의원 목록 조회
    legislators = legislator_service.filter_legislators(
        db, 
        name=name, 
        party=party, 
        district=district, 
        term=term
    )
    
    # 템플릿 렌더링
    return templates.TemplateResponse(
        "champions/list.html", 
        {
            "request": request, 
            "legislators": legislators,
            "filter_options": filter_options,
            "current_filters": {
                "name": name,
                "party": party,
                "district": district,
                "term": term
            }
        }
    )

@router.get("/champions/{legislator_id}")
async def champion_detail(
    legislator_id: int, 
    request: Request, 
    db: Session = Depends(get_db), 
    tab: str = "basic_info"
):
    # 의원 상세 정보 조회
    legislator = legislator_service.get_legislator_detail(db, legislator_id)
    if not legislator:
        # 의원 정보가 없는 경우 404 에러
        return templates.TemplateResponse(
            "404.html", 
            {"request": request, "message": "해당 의원 정보를 찾을 수 없습니다."}
        )
    
    # 의원 스탯 정보 조회
    stats = legislator_service.get_legislator_stats(db, legislator_id)
    
    # 평균 스탯 조회
    avg_stats = stats_service.get_average_stats(db)
    
    # 비교 차트 데이터 생성
    chart_data = chart_service.generate_comparison_chart_data(stats, avg_stats)
    
    # 탭별 추가 정보 조회
    tab_data = {}
    
    if tab == "basic_info":
        # SNS 정보 조회
        tab_data["sns"] = legislator_service.get_legislator_sns(db, legislator_id)
        # 위원회 경력 조회
        tab_data["committee_history"] = legislator_service.get_legislator_committee_history(db, legislator_id)
    elif tab == "tendency":
        # 발언 키워드 TOP 10 조회
        from app.services import speech_service, vote_service
        
        # 발언 키워드 및 차트 데이터
        tab_data["top_keywords"] = speech_service.get_top_keywords(db, legislator_id)
        tab_data["keyword_chart"] = chart_service.generate_keyword_chart_data(tab_data["top_keywords"])
        
        # 회의 구분별 발언 수 및 차트 데이터
        tab_data["speeches_by_meeting"] = speech_service.get_speech_by_meeting_type(db, legislator_id)
        tab_data["speech_chart"] = chart_service.generate_speech_chart_data(tab_data["speeches_by_meeting"])
        
        # 본회의 표결 결과 조회
        tab_data["vote_results"] = vote_service.get_vote_results(db, legislator_id)
    elif tab == "bills":
        from app.services import bill_service
        tab_data["representative_bills"] = bill_service.get_representative_bills(db, legislator_id)
    elif tab == "co_bills":
        # 공동발의안 목록 조회
        from app.services import bill_service
        tab_data["co_bills"] = bill_service.get_co_sponsored_bills(db, legislator_id)
    
    # 템플릿 렌더링
    return templates.TemplateResponse(
        "champions/detail.html", 
        {
            "request": request, 
            "legislator": legislator,
            "stats": stats,
            "avg_stats": avg_stats,
            "chart_data": chart_data,
            "tab": tab,
            "tab_data": tab_data
        }
    )