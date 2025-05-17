from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.models.legislator import Legislator
from app.models.committee import Committee
from app.services import stats_service, chart_service

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/misc-ranking")
async def misc_ranking_home(request: Request, db: Session = Depends(get_db)):
    """
    잡다한 랭킹 홈 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
    
    Returns:
        템플릿 렌더링 응답
    """
    # 정당별 평균 재산 조회
    party_asset_stats = stats_service.get_party_average_stats(db, stat='asset')
    
    # 초선/재선별 평균 점수 조회
    term_score_stats = stats_service.get_term_average_stats(db, stat='overall_score')
    
    # 차트 데이터 생성
    party_asset_chart = chart_service.generate_party_asset_chart_data(party_asset_stats)
    term_score_chart = chart_service.generate_term_score_chart_data(term_score_stats)
    
    # 템플릿 렌더링
    return templates.TemplateResponse(
        "misc_ranking/index.html", 
        {
            "request": request,
            "party_asset_stats": party_asset_stats,
            "term_score_stats": term_score_stats,
            "party_asset_chart": party_asset_chart,
            "term_score_chart": term_score_chart
        }
    )

@router.get("/misc-ranking/party")
async def party_ranking(request: Request, db: Session = Depends(get_db), party_name: Optional[str] = None):
    """
    정당별 랭킹 페이지
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        party_name: 선택한 정당명 (선택 사항)
    
    Returns:
        템플릿 렌더링
    """
    # 정당 목록 미리 조회 (공통)
    party_query = db.query(Legislator.poly_nm).distinct().all()
    parties = [party[0] for party in party_query]
    
    # 정당별 평균 종합점수 조회 (항상 필요)
    party_scores = stats_service.get_party_average_scores(db)
    
    # 정당별 평균 대표발의안수 조회 (항상 필요)
    party_bills = stats_service.get_party_average_bill_counts(db)
    
    # 차트 데이터 생성 (항상 필요)
    scores_chart = chart_service.generate_party_scores_chart_data(party_scores)
    bills_chart = chart_service.generate_party_bills_chart_data(party_bills)
    
    # 기본 컨텍스트 데이터
    context = {
        "request": request,
        "parties": parties,
        "party_name": party_name,
        "party_scores": party_scores,
        "party_bills": party_bills,
        "scores_chart": scores_chart,
        "bills_chart": bills_chart
    }
    
    # 특정 정당이 선택된 경우 추가 데이터 조회
    if party_name:
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
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "party_stats": party_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/party.html", context)

@router.get("/misc-ranking/committee")
async def committee_ranking(request: Request, db: Session = Depends(get_db), committee_name: Optional[str] = None):
    """
    위원회별 랭킹 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        committee_name: 선택한 위원회명 (None인 경우 위원회 비교 홈 화면)
    
    Returns:
        템플릿 렌더링 응답
    """
    # 위원회 목록 미리 조회 (공통)
    committee_query = db.query(Committee.dept_nm).distinct().all()
    committees = [committee[0] for committee in committee_query]
    
    # 위원회별 처리 비율 조회 - 항상 필요
    processing_ratios = stats_service.get_committee_processing_ratio(db)
    
    # 위원회별 평균 점수 조회 - 항상 필요
    committee_scores = stats_service.get_committee_average_scores(db)
    
    # 차트 데이터 생성 - 항상 필요
    processing_chart = chart_service.generate_committee_processing_chart_data(processing_ratios)
    scores_chart = chart_service.generate_committee_scores_chart_data(committee_scores)
    
    # 기본 컨텍스트 데이터
    context = {
        "request": request,
        "committees": committees,
        "committee_name": committee_name,
        "processing_ratios": processing_ratios,
        "committee_scores": committee_scores,
        "processing_chart": processing_chart,
        "scores_chart": scores_chart
    }
    
    # 특정 위원회가 선택된 경우 추가 데이터 조회
    if committee_name:
        # 위원회명이 유효한지 확인
        if committee_name not in committees:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{committee_name}'라는 위원회를 찾을 수 없습니다."}
            )
        
        # 위원회 통계 요약 조회
        committee_stats = stats_service.get_committee_stats_summary(db, committee_name)
        
        # 위원회 소속 의원 목록 조회
        legislators = stats_service.get_legislators_by_committee(db, committee_name)
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "committee_stats": committee_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/committee.html", context)

@router.get("/misc-ranking/term")
async def term_ranking(request: Request, db: Session = Depends(get_db), term: Optional[str] = None):
    """
    초선/재선 랭킹 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        term: 선택한 선수 (None인 경우 전체 보기)
    
    Returns:
        템플릿 렌더링 응답
    """
    # 초선/재선 목록 미리 조회 (공통)
    term_query = db.query(Legislator.reele_gbn_nm).distinct().all()
    terms = [term[0] for term in term_query if term[0]]
    
    # 선수별 티어 분포 조회 (항상 필요)
    tier_distribution = stats_service.get_tier_distribution_by_term(db)
    
    # 선수별 평균 재산 조회 (항상 필요)
    term_assets = stats_service.get_term_average_assets(db)
    
    # 차트 데이터 생성 (항상 필요)
    tier_chart = chart_service.generate_term_tier_chart_data(tier_distribution)
    asset_chart = chart_service.generate_term_asset_chart_data(term_assets)
    
    # 기본 컨텍스트 데이터
    context = {
        "request": request,
        "terms": terms,
        "term": term,
        "tier_distribution": tier_distribution,
        "term_assets": term_assets,
        "tier_chart": tier_chart,
        "asset_chart": asset_chart
    }
    
    # 특정 선수가 선택된 경우 추가 데이터 조회
    if term:
        # 선수가 유효한지 확인
        if term not in terms:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{term}'(이)라는 선수를 찾을 수 없습니다."}
            )
        
        # 선수별 통계 요약 조회
        term_stats = stats_service.get_term_stats_summary(db, term)
        
        # 해당 선수 의원 목록 조회
        legislators = stats_service.get_legislators_by_term(db, term)
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "term_stats": term_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/term.html", context)

@router.get("/misc-ranking/age")
async def age_ranking(request: Request, db: Session = Depends(get_db), age_group: Optional[str] = None):
    """
    나이별 랭킹 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        age_group: 선택한 나이대 (None인 경우 나이대별 비교 홈 화면)
    
    Returns:
        템플릿 렌더링 응답
    """
    # 나이대 목록 정의
    age_groups = ["30대 이하", "40대", "50대", "60대", "70대 이상"]
    
    # 나이대별 평균 점수 조회 - 항상 필요
    age_scores = stats_service.get_age_average_scores(db)
    
    # 나이대별 평균 재산 조회 - 항상 필요
    age_assets = stats_service.get_age_average_assets(db)
    
    # 차트 데이터 생성 - 항상 필요
    score_chart = chart_service.generate_age_score_chart_data(age_scores)
    asset_chart = chart_service.generate_age_asset_chart_data(age_assets)
    
    # 기본 컨텍스트 데이터
    context = {
        "request": request,
        "age_groups": age_groups,
        "age_group": age_group,
        "age_scores": age_scores,
        "age_assets": age_assets,
        "score_chart": score_chart,
        "asset_chart": asset_chart
    }
    
    # 특정 나이대가 선택된 경우 추가 데이터 조회
    if age_group:
        # 나이대가 유효한지 확인
        if age_group not in age_groups:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{age_group}'(이)라는 나이대를 찾을 수 없습니다."}
            )
        
        # 나이대별 통계 요약 조회
        age_stats = stats_service.get_age_stats_summary(db, age_group)
        
        # 해당 나이대 의원 목록 조회
        legislators = stats_service.get_legislators_by_age_group(db, age_group)
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "age_stats": age_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/age.html", context)

@router.get("/misc-ranking/gender")
async def gender_ranking(request: Request, db: Session = Depends(get_db), gender: Optional[str] = None):
    """
    성별 랭킹 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        gender: 선택한 성별 (None인 경우 성별 비교 홈 화면)
    
    Returns:
        템플릿 렌더링 응답
    """
    # 성별 목록 미리 조회 (공통)
    gender_query = db.query(Legislator.sex_gbn_nm).distinct().all()
    genders = [gender[0] for gender in gender_query if gender[0]]
    
    # 성별 티어 분포 조회 (항상 필요)
    tier_distribution = stats_service.get_tier_distribution_by_gender(db)
    
    # 성별 평균 재산 조회 (항상 필요)
    gender_assets = stats_service.get_gender_average_assets(db)
    
    # 차트 데이터 생성 (항상 필요)
    tier_chart = chart_service.generate_gender_tier_chart_data(tier_distribution)
    asset_chart = chart_service.generate_gender_asset_chart_data(gender_assets)
    
    # 기본 컨텍스트 데이터
    context = {
        "request": request,
        "genders": genders,
        "gender": gender,
        "tier_distribution": tier_distribution,
        "gender_assets": gender_assets,
        "tier_chart": tier_chart,
        "asset_chart": asset_chart
    }
    
    # 특정 성별이 선택된 경우 추가 데이터 조회
    if gender:
        # 성별이 유효한지 확인
        if gender not in genders:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{gender}'(이)라는 성별을 찾을 수 없습니다."}
            )
        
        # 성별 통계 요약 조회
        gender_stats = stats_service.get_gender_stats_summary(db, gender)
        
        # 해당 성별 의원 목록 조회
        legislators = stats_service.get_legislators_by_gender(db, gender)
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "gender_stats": gender_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/gender.html", context)

@router.get("/misc-ranking/asset")
async def asset_ranking(request: Request, db: Session = Depends(get_db), asset_group: Optional[str] = None):
    """
    재산 랭킹 화면 처리
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        asset_group: 선택한 재산 구간 (None인 경우 전체 비교 홈 화면)
    
    Returns:
        템플릿 렌더링 응답
    """
    # 재산 구간 목록 정의
    asset_groups = ["1억 미만", "1억~10억", "10억~50억", "50억~100억", "100억 이상"]
    
    # 점수-재산 상관관계 조회 (항상 필요)
    correlation_data = stats_service.get_score_asset_correlation(db)
    
    # 정당별 재산 비율 조회 (항상 필요)
    party_asset_ratio = stats_service.get_party_asset_ratio(db)
    
    # 차트 데이터 생성 (항상 필요)
    correlation_chart = chart_service.generate_score_asset_correlation_chart_data(correlation_data)
    party_ratio_chart = chart_service.generate_party_asset_ratio_chart_data(party_asset_ratio)
    
    # 기본 컨텍스트 데이터 (항상 필요)
    context = {
        "request": request,
        "asset_groups": asset_groups,
        "asset_group": asset_group,
        "correlation_data": correlation_data,
        "party_asset_ratio": party_asset_ratio,
        "correlation_chart": correlation_chart,
        "party_ratio_chart": party_ratio_chart
    }
    
    # asset_group이 지정된 경우 - 특정 재산 구간 상세 화면
    if asset_group:
        # 재산 구간이 유효한지 확인
        if asset_group not in asset_groups:
            # 유효하지 않은 경우 404 에러
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"'{asset_group}'(이)라는 재산 구간을 찾을 수 없습니다."}
            )
        
        # 재산 구간별 통계 요약 조회
        asset_stats = stats_service.get_asset_stats_summary(db, asset_group)
        
        # 해당 재산 구간 의원 목록 조회
        legislators = stats_service.get_legislators_by_asset_group(db, asset_group)
        
        # 컨텍스트에 추가 데이터 추가
        context.update({
            "asset_stats": asset_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/asset.html", context)