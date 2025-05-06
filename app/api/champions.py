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
        # 현재는 구현하지 않음 - 향후 구현
        pass
    elif tab == "bills":
        # 현재는 구현하지 않음 - 향후 구현
        pass
    elif tab == "co_bills":
        # 현재는 구현하지 않음 - 향후 구현
        pass
    
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