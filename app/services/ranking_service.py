from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.models.legislator import Legislator

def get_top_legislators(db: Session, count: int = 5, category: str = 'overall') -> List[Dict[str, Any]]:
    """
    특정 카테고리 기준 상위 N명의 국회의원을 조회하는 함수
    
    Args:
        db: 데이터베이스 세션
        count: 조회할 상위 의원 수 (기본값: 5)
        category: 랭킹 카테고리 (기본값: 'overall')
    
    Returns:
        상위 N명 국회의원 정보 리스트
    """
    # 카테고리에 따른 정렬 기준 설정
    if category == 'overall':
        sort_column = Legislator.overall_score
    elif category == 'participation':
        sort_column = Legislator.participation_score
    elif category == 'legislation':
        sort_column = Legislator.legislation_score
    elif category == 'speech':
        sort_column = Legislator.speech_score
    elif category == 'voting':
        sort_column = Legislator.voting_score
    elif category == 'cooperation':
        sort_column = Legislator.cooperation_score
    else:
        sort_column = Legislator.overall_score  # 기본값
    
    # 데이터베이스 쿼리 실행 - 높은 점수순으로 정렬
    legislators = db.query(Legislator) \
        .order_by(sort_column.desc()) \
        .limit(count) \
        .all()
    
    # ORM 객체를 dict로 변환하여 반환
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

def calculate_overall_scores(db: Session) -> None:
    # 호출: db.query(Legislator)로 모든 의원 조회
    # 호출: services.data_processing.process_attendance_data() 등 데이터 처리 함수들
    # 각 카테고리별 점수를 가중치 적용하여 합산
    # 호출: db.commit()으로 DB에 변경사항 저장
    pass

def update_rankings(db: Session) -> None:
    # 호출: db.query(Legislator)로 종합 점수 기준 의원 정렬
    # 랭킹 번호 할당
    # 호출: db.commit()으로 DB에 변경사항 저장
    pass

def get_bottom_legislators(db: Session, count: int = 5, category: str = 'overall') -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 특정 카테고리 기준 하위 N명 조회
    # 반환: 의원 목록
    pass

def get_legislators_by_filter(
    db: Session,
    category: str = 'overall', 
    party: Optional[str] = None,
    committee: Optional[str] = None,
    term: Optional[str] = None,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    asset_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 기본 쿼리 시작
    # 필터 조건에 따라 쿼리 구성
    # 카테고리에 따라 정렬 기준 변경
    # 반환: 필터링된 의원 목록
    pass