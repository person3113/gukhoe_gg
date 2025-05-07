from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.models.legislator import Legislator
from app.services import stats_service, chart_service

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/misc-ranking")
async def misc_ranking_home(request: Request, db: Session = Depends(get_db)):
    # 호출: stats_service.get_party_average_stats(stat='asset')로 정당별 평균 재산 조회
    # 호출: stats_service.get_term_average_stats(stat='overall_score')로 초선/재선별 평균 점수 조회
    # 호출: chart_service.generate_party_asset_chart_data()로 정당별 평균 재산 차트 데이터 생성
    # 호출: chart_service.generate_term_score_chart_data()로 초선/재선별 평균 점수 차트 데이터 생성
    # 반환: 템플릿 렌더링(misc_ranking/index.html)
    pass

@router.get("/misc-ranking/party")
async def party_ranking(request: Request, db: Session = Depends(get_db), party_name: Optional[str] = None):
    """
    정당별 랭킹 페이지
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        party_name: 선택한 정당명 (None인 경우 정당 비교 홈 화면)
    
    Returns:
        템플릿 렌더링
    """
    # 정당 목록 미리 조회 (공통)
    party_query = db.query(Legislator.poly_nm).distinct().all()
    parties = [party[0] for party in party_query]
    
    # party_name이 None인 경우 - 정당 비교 홈 화면
    if party_name is None:
        # 정당별 평균 종합점수 조회
        party_scores = stats_service.get_party_average_scores(db)
        
        # 정당별 평균 대표발의안수 조회
        party_bills = stats_service.get_party_average_bill_counts(db)
        
        # 차트 데이터 생성
        scores_chart = chart_service.generate_party_scores_chart_data(party_scores)
        bills_chart = chart_service.generate_party_bills_chart_data(party_bills)
        
        # 템플릿 렌더링
        return templates.TemplateResponse(
            "misc_ranking/party.html", 
            {
                "request": request,
                "parties": parties,
                "party_name": None,
                "party_scores": party_scores,
                "party_bills": party_bills,
                "scores_chart": scores_chart,
                "bills_chart": bills_chart
            }
        )
    else:
        # 정당명이 유효한지 확인
        if party_name not in parties:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{party_name}'이라는 정당을 찾을 수 없습니다."}
            )
        
        # 정당 통계 요약 조회
        party_stats = stats_service.get_party_stats_summary(db, party_name)
        
        # 정당 소속 의원 목록 조회
        legislators = stats_service.get_legislators_by_party(db, party_name)
        
        # 템플릿 렌더링
        return templates.TemplateResponse(
            "misc_ranking/party.html", 
            {
                "request": request,
                "parties": parties,
                "party_name": party_name,
                "party_stats": party_stats,
                "legislators": legislators
            }
        )

@router.get("/misc-ranking/committee")
async def committee_ranking(request: Request, db: Session = Depends(get_db), committee_name: Optional[str] = None):
    # committee_name이 None인 경우 - 위원회 비교 홈 화면
    if committee_name is None:
        # 호출: stats_service.get_committee_processing_ratio()로 위원회별 처리 비율 조회
        # 호출: stats_service.get_committee_average_scores()로 위원회별 평균 점수 조회
        # 호출: chart_service.generate_committee_processing_chart_data()로 차트 데이터 생성
        # 호출: chart_service.generate_committee_scores_chart_data()로 차트 데이터 생성
        pass
    else:
        # 호출: stats_service.get_committee_stats_summary(committee_name)로 위원회 통계 요약 조회
        # 호출: stats_service.get_legislators_by_committee(committee_name)로 위원회 소속 의원 목록 조회
        pass

    # 반환: 템플릿 렌더링(misc_ranking/committee.html)
    pass

@router.get("/misc-ranking/term")
async def term_ranking(request: Request, db: Session = Depends(get_db), term: Optional[str] = None):
    # term이 None인 경우 - 초선/재선 비교 홈 화면
    if term is None:
        # 호출: stats_service.get_tier_distribution_by_term()로 선수별 티어 분포 조회
        # 호출: stats_service.get_term_average_assets()로 선수별 평균 재산 조회
        # 호출: chart_service.generate_term_tier_chart_data()로 차트 데이터 생성
        # 호출: chart_service.generate_term_asset_chart_data()로 차트 데이터 생성
        pass
    else:
        # 호출: stats_service.get_term_stats_summary(term)로 선수별 통계 요약 조회
        # 호출: stats_service.get_legislators_by_term(term)로 특정 선수 의원 목록 조회
        pass

    # 반환: 템플릿 렌더링(misc_ranking/term.html)
    pass

@router.get("/misc-ranking/age")
async def age_ranking(request: Request, db: Session = Depends(get_db), age_group: Optional[str] = None):
    # age_group이 None인 경우 - 나이별 비교 홈 화면
    if age_group is None:
        # 호출: stats_service.get_age_average_scores()로 나이대별 평균 점수 조회
        # 호출: stats_service.get_age_average_assets()로 나이대별 평균 재산 조회
        # 호출: chart_service.generate_age_score_chart_data()로 차트 데이터 생성
        # 호출: chart_service.generate_age_asset_chart_data()로 차트 데이터 생성
        pass
    else:
        # 호출: stats_service.get_age_stats_summary(age_group)로 나이대별 통계 요약 조회
        # 호출: stats_service.get_legislators_by_age_group(age_group)로 특정 나이대 의원 목록 조회
        pass

    # 반환: 템플릿 렌더링(misc_ranking/age.html)
    pass

@router.get("/misc-ranking/gender")
async def gender_ranking(request: Request, db: Session = Depends(get_db), gender: Optional[str] = None):
    # gender가 None인 경우 - 성별 비교 홈 화면
    if gender is None:
        # 호출: stats_service.get_tier_distribution_by_gender()로 성별 티어 분포 조회
        # 호출: stats_service.get_gender_average_assets()로 성별 평균 재산 조회
        # 호출: chart_service.generate_gender_tier_chart_data()로 차트 데이터 생성
        # 호출: chart_service.generate_gender_asset_chart_data()로 차트 데이터 생성
        pass
    else:
        # 호출: stats_service.get_gender_stats_summary(gender)로 성별 통계 요약 조회
        # 호출: stats_service.get_legislators_by_gender(gender)로 특정 성별 의원 목록 조회
        pass

    # 반환: 템플릿 렌더링(misc_ranking/gender.html)
    pass

@router.get("/misc-ranking/asset")
async def asset_ranking(request: Request, db: Session = Depends(get_db), asset_group: Optional[str] = None):
    # asset_group이 None인 경우 - 재산 비교 홈 화면
    if asset_group is None:
        # 호출: stats_service.get_score_asset_correlation()로 점수-재산 상관관계 조회
        # 호출: stats_service.get_party_asset_ratio()로 정당별 재산 비율 조회
        # 호출: chart_service.generate_score_asset_correlation_chart_data()로 차트 데이터 생성
        # 호출: chart_service.generate_party_asset_ratio_chart_data()로 차트 데이터 생성
        pass
    else:
        # 호출: stats_service.get_asset_stats_summary(asset_group)로 재산 구간별 통계 요약 조회
        # 호출: stats_service.get_legislators_by_asset_group(asset_group)로 특정 재산 구간 의원 목록 조회
        pass

    # 반환: 템플릿 렌더링(misc_ranking/asset.html)
    pass