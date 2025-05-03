from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services import legislator_service, stats_service, chart_service, bill_service, speech_service, vote_service

router = APIRouter()

@router.get("/champions")
async def list_champions(
    request: Request, 
    db: Session = Depends(get_db), 
    name: Optional[str] = None, 
    party: Optional[str] = None, 
    district: Optional[str] = None, 
    term: Optional[str] = None
):
    # 호출: legislator_service.get_filter_options()로 필터 옵션 가져오기
    # 호출: legislator_service.filter_legislators()로 필터링된 의원 목록 조회
    # 반환: 템플릿 렌더링(champions/list.html)
    pass

@router.get("/champions/{legislator_id}")
async def champion_detail(
    legislator_id: int, 
    request: Request, 
    db: Session = Depends(get_db), 
    tab: str = "basic_info"
):
    # 호출: legislator_service.get_legislator_detail()로 의원 상세 정보 조회
    # 호출: legislator_service.get_legislator_stats()로 의원 스탯 정보 조회
    # 호출: stats_service.get_average_stats()로 평균 스탯 조회
    # 호출: chart_service.generate_comparison_chart_data()로 비교 차트 데이터 생성

    # tab 값에 따라 다른 서비스 호출
    if tab == "basic_info":
        # 호출: legislator_service.get_legislator_basic_info()
        # 호출: legislator_service.get_legislator_sns()
        # 호출: legislator_service.get_legislator_committee_history()
        pass
    elif tab == "tendency":
        # 호출: speech_service.get_top_keywords()
        # 호출: speech_service.get_speech_by_meeting_type()
        # 호출: vote_service.get_vote_results()
        # 호출: chart_service.generate_keyword_chart_data()
        # 호출: chart_service.generate_speech_chart_data()
        pass
    elif tab == "bills":
        # 호출: bill_service.get_representative_bills()
        pass
    elif tab == "co_bills":
        # 호출: bill_service.get_co_sponsored_bills()
        pass

    # 반환: 탭에 따른 템플릿 렌더링(champions/detail.html)
    pass