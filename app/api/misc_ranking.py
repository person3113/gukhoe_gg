from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.db.database import get_db
from app.services import stats_service, chart_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/misc-ranking")
async def misc_ranking_home(request: Request, db: Session = Depends(get_db)):
    """
    잡다한 랭킹 홈 화면
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        
    Returns:
        잡다한 랭킹 홈 화면 템플릿 렌더링
    """
    # 1. 정당별 평균 재산 조회
    party_assets = stats_service.get_party_average_stats(db, stat='asset')
    
    # 2. 초선/재선별 평균 종합점수 조회
    term_scores = stats_service.get_term_average_stats(db, stat='overall_score')
    
    # 3. 차트 데이터 생성
    party_asset_chart = chart_service.generate_party_asset_chart_data(party_assets)
    term_score_chart = chart_service.generate_term_score_chart_data(term_scores)
    
    # 4. 템플릿 렌더링
    return templates.TemplateResponse(
        "misc_ranking/index.html",
        {
            "request": request,
            "current_tab": "misc_ranking",
            "party_assets": party_assets,
            "term_scores": term_scores,
            "party_asset_chart": party_asset_chart,
            "term_score_chart": term_score_chart
        }
    )

@router.get("/misc-ranking/party")
async def party_ranking(request: Request, db: Session = Depends(get_db), party_name: Optional[str] = None):
    """
    정당별 랭킹 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        party_name: 정당명 (None인 경우 정당 비교 화면)
        
    Returns:
        정당별 랭킹 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 설정
    context = {
        "request": request,
        "current_tab": "party"
    }
    
    # party_name이 None인 경우 - 정당 비교 홈 화면
    if party_name is None:
        # 1. 정당별 평균 종합점수 조회
        party_scores = stats_service.get_party_average_scores(db)
        
        # 2. 정당별 평균 대표발의안수 조회
        party_bills = stats_service.get_party_average_bill_counts(db)
        
        # 3. 차트 데이터 생성
        scores_chart = chart_service.generate_party_scores_chart_data(party_scores)
        bills_chart = chart_service.generate_party_bills_chart_data(party_bills)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "party_scores": party_scores,
            "party_bills": party_bills,
            "scores_chart": scores_chart,
            "bills_chart": bills_chart
        })
    else:
        # 1. 정당 통계 요약 조회
        party_stats = stats_service.get_party_stats_summary(db, party_name)
        
        # 정당이 존재하지 않는 경우 404 오류 반환
        if not party_stats:
            return templates.TemplateResponse(
                "404.html",
                {
                    "request": request,
                    "message": f"'{party_name}' 정당을 찾을 수 없습니다."
                }
            )
        
        # 2. 정당 소속 의원 목록 조회
        legislators = stats_service.get_legislators_by_party(db, party_name)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "party_name": party_name,
            "party_stats": party_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/party.html", context)

@router.get("/misc-ranking/committee")
async def committee_ranking(request: Request, db: Session = Depends(get_db), committee_name: Optional[str] = None):
    """
    위원회별 랭킹 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        committee_name: 위원회명 (None인 경우 위원회 비교 화면)
        
    Returns:
        위원회별 랭킹 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 설정
    context = {
        "request": request,
        "current_tab": "committee"
    }
    
    # committee_name이 None인 경우 - 위원회 비교 홈 화면
    if committee_name is None:
        # 1. 위원회별 처리 비율 조회
        processing_ratios = stats_service.get_committee_processing_ratio(db)
        
        # 2. 위원회별 평균 종합점수 조회
        committee_scores = stats_service.get_committee_average_scores(db)
        
        # 3. 차트 데이터 생성
        processing_chart = chart_service.generate_committee_processing_chart_data(processing_ratios)
        scores_chart = chart_service.generate_committee_scores_chart_data(committee_scores)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "processing_ratios": processing_ratios,
            "committee_scores": committee_scores,
            "processing_chart": processing_chart,
            "scores_chart": scores_chart
        })
    else:
        # 1. 위원회 통계 요약 조회
        committee_stats = stats_service.get_committee_stats_summary(db, committee_name)
        
        # 위원회가 존재하지 않는 경우 404 오류 반환
        if not committee_stats:
            return templates.TemplateResponse(
                "404.html",
                {
                    "request": request,
                    "message": f"'{committee_name}' 위원회를 찾을 수 없습니다."
                }
            )
        
        # 2. 위원회 소속 의원 목록 조회
        legislators = stats_service.get_legislators_by_committee(db, committee_name)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "committee_name": committee_name,
            "committee_stats": committee_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/committee.html", context)

@router.get("/misc-ranking/term")
async def term_ranking(request: Request, db: Session = Depends(get_db), term: Optional[str] = None):
    """
    초선/재선별 랭킹 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        term: 초선/재선 구분 (None인 경우 초선/재선 비교 화면)
        
    Returns:
        초선/재선별 랭킹 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 설정
    context = {
        "request": request,
        "current_tab": "term"
    }
    
    # term이 None인 경우 - 초선/재선 비교 홈 화면
    if term is None:
        # 1. 선수별 티어 분포 조회
        tier_distribution = stats_service.get_tier_distribution_by_term(db)
        
        # 2. 선수별 평균 재산 조회
        term_assets = stats_service.get_term_average_assets(db)
        
        # 3. 차트 데이터 생성
        tier_chart = chart_service.generate_term_tier_chart_data(tier_distribution)
        asset_chart = chart_service.generate_term_asset_chart_data(term_assets)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "tier_distribution": tier_distribution,
            "term_assets": term_assets,
            "tier_chart": tier_chart,
            "asset_chart": asset_chart
        })
    else:
        # 1. 특정 선수 통계 요약 조회
        term_stats = stats_service.get_term_stats_summary(db, term)
        
        # 선수 값이 유효하지 않은 경우 404 오류 반환
        if not term_stats:
            return templates.TemplateResponse(
                "404.html",
                {
                    "request": request,
                    "message": f"'{term}' 선수를 찾을 수 없습니다."
                }
            )
        
        # 2. 특정 선수 의원 목록 조회
        legislators = stats_service.get_legislators_by_term(db, term)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "term": term,
            "term_stats": term_stats,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/term.html", context)

@router.get("/misc-ranking/gender")
async def gender_ranking(request: Request, db: Session = Depends(get_db), gender: Optional[str] = None):
    """
    성별에 따른 국회의원 통계 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        gender: 성별 파라미터 (None, "남", "여")
    
    Returns:
        성별 통계 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 초기화
    context = {
        "request": request,
        "current_tab": "gender"
    }
    
    # gender가 None인 경우 - 성별 비교 홈 화면
    if gender is None:
        # 1. 성별 티어 분포 데이터 조회
        tier_distribution = stats_service.get_tier_distribution_by_gender(db)
        
        # 2. 성별 평균 재산 데이터 조회
        average_assets = stats_service.get_gender_average_assets(db)
        
        # 3. 차트 데이터 생성
        tier_chart_data = chart_service.generate_gender_tier_chart_data(tier_distribution)
        asset_chart_data = chart_service.generate_gender_asset_chart_data(average_assets)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "tier_distribution": tier_distribution,
            "average_assets": average_assets,
            "tier_chart_data": tier_chart_data,
            "asset_chart_data": asset_chart_data
        })
    else:
        # 유효한 성별인지 확인 (남 또는 여)
        valid_genders = ["남", "여"]
        if gender not in valid_genders:
            # 404 에러 페이지 반환
            return templates.TemplateResponse(
                "404.html", 
                {
                    "request": request, 
                    "message": f"'{gender}'는 유효한 성별이 아닙니다. '남' 또는 '여'를 선택해주세요."
                }
            )
        
        # 1. 성별 통계 요약 조회
        stats_summary = stats_service.get_gender_stats_summary(db, gender)
        
        # 2. 성별 의원 목록 조회
        legislators = stats_service.get_legislators_by_gender(db, gender)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "gender": gender,
            "stats_summary": stats_summary,
            "legislators": legislators
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/gender.html", context)

@router.get("/misc-ranking/age")
async def age_ranking(request: Request, db: Session = Depends(get_db), age_group: Optional[str] = None):
    """
    나이대별 랭킹 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        age_group: 나이대 구분 (None, "30대 이하", "40대", "50대", "60대", "70대 이상")
        
    Returns:
        나이대별 랭킹 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 설정
    context = {
        "request": request,
        "current_tab": "age"
    }
    
    # 유효한 나이대 목록
    valid_age_groups = ["30대 이하", "40대", "50대", "60대", "70대 이상"]
    
    # age_group이 None인 경우 - 나이대 비교 홈 화면
    if age_group is None:
        # 1. 나이대별 평균 종합점수 조회
        age_scores = stats_service.get_age_average_scores(db)
        
        # 2. 나이대별 평균 재산 조회
        age_assets = stats_service.get_age_average_assets(db)
        
        # 3. 차트 데이터 생성
        score_chart = chart_service.generate_age_score_chart_data(age_scores)
        asset_chart = chart_service.generate_age_asset_chart_data(age_assets)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "age_scores": age_scores,
            "age_assets": age_assets,
            "score_chart": score_chart,
            "asset_chart": asset_chart,
            "valid_age_groups": valid_age_groups
        })
    else:
        # 나이대가 유효한지 확인
        if age_group not in valid_age_groups:
            return templates.TemplateResponse(
                "404.html",
                {
                    "request": request,
                    "message": f"'{age_group}'는 유효한 나이대가 아닙니다."
                }
            )
        
        # 1. 나이대별 통계 요약 조회
        age_stats = stats_service.get_age_stats_summary(db, age_group)
        
        # 2. 나이대별 의원 목록 조회
        legislators = stats_service.get_legislators_by_age_group(db, age_group)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "age_group": age_group,
            "age_stats": age_stats,
            "legislators": legislators,
            "valid_age_groups": valid_age_groups
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/age.html", context)

@router.get("/misc-ranking/asset")
async def asset_ranking(request: Request, db: Session = Depends(get_db), asset_group: Optional[str] = None):
    """
    재산별 랭킹 페이지 렌더링
    
    Args:
        request: FastAPI 요청 객체
        db: 데이터베이스 세션
        asset_group: 재산 구간 (None, "1억 미만", "1~10억", "10~50억", "50~100억", "100억 이상")
        
    Returns:
        재산별 랭킹 화면 템플릿 렌더링
    """
    # 공통 컨텍스트 데이터 설정
    context = {
        "request": request,
        "current_tab": "asset"
    }
    
    # 유효한 재산 구간 목록
    valid_asset_groups = ["1억 미만", "1~10억", "10~50억", "50~100억", "100억 이상"]
    
    # asset_group이 None인 경우 - 재산 비교 홈 화면
    if asset_group is None:
        # 1. 점수와 재산의 상관관계 데이터 조회
        correlation_data = stats_service.get_score_asset_correlation(db)
        
        # 2. 정당별 재산 비율 조회
        party_asset_ratio = stats_service.get_party_asset_ratio(db)
        
        # 3. 차트 데이터 생성
        correlation_chart = chart_service.generate_score_asset_correlation_chart_data(correlation_data)
        ratio_chart = chart_service.generate_party_asset_ratio_chart_data(party_asset_ratio)
        
        # 4. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "comparison",
            "correlation_data": correlation_data,
            "party_asset_ratio": party_asset_ratio,
            "correlation_chart": correlation_chart,
            "ratio_chart": ratio_chart,
            "valid_asset_groups": valid_asset_groups
        })
    else:
        # 재산 구간이 유효한지 확인
        if asset_group not in valid_asset_groups:
            return templates.TemplateResponse(
                "404.html",
                {
                    "request": request,
                    "message": f"'{asset_group}'는 유효한 재산 구간이 아닙니다."
                }
            )
        
        # 1. 재산 구간별 통계 요약 조회
        asset_stats = stats_service.get_asset_stats_summary(db, asset_group)
        
        # 2. 재산 구간별 의원 목록 조회
        legislators = stats_service.get_legislators_by_asset_group(db, asset_group)
        
        # 3. 컨텍스트에 데이터 추가
        context.update({
            "view_type": "detail",
            "asset_group": asset_group,
            "asset_stats": asset_stats,
            "legislators": legislators,
            "valid_asset_groups": valid_asset_groups
        })
    
    # 템플릿 렌더링
    return templates.TemplateResponse("misc_ranking/asset.html", context)