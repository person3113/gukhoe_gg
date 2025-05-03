from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import CommitteeHistory

def get_filter_options(db: Session) -> Dict[str, List[str]]:
    """
    필터 옵션(정당, 선거구, 초선/재선) 데이터 조회
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        필터 옵션 딕셔너리
    """
    # 정당 목록 조회
    parties = db.query(Legislator.poly_nm).distinct().all()
    party_list = [party[0] for party in parties]
    
    # 선거구 목록 조회
    districts = db.query(Legislator.orig_nm).distinct().all()
    district_list = [district[0] for district in districts]
    
    # 초선/재선 목록 조회
    terms = db.query(Legislator.reele_gbn_nm).distinct().all()
    term_list = [term[0] for term in terms]
    
    # 필터 옵션 딕셔너리 생성
    filter_options = {
        "parties": party_list,
        "districts": district_list,
        "terms": term_list
    }
    
    return filter_options

def filter_legislators(
    db: Session, 
    name: Optional[str] = None,
    party: Optional[str] = None,
    district: Optional[str] = None,
    term: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    조건에 맞는 국회의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        name: 이름 검색어 (선택)
        party: 정당 필터 (선택)
        district: 선거구 필터 (선택)
        term: 초선/재선 필터 (선택)
    
    Returns:
        필터링된 국회의원 목록
    """
    # 기본 쿼리
    query = db.query(Legislator)
    
    # 필터 조건 적용
    if name:
        query = query.filter(Legislator.hg_nm.like(f'%{name}%'))
    
    if party:
        query = query.filter(Legislator.poly_nm == party)
    
    if district:
        query = query.filter(Legislator.orig_nm == district)
    
    if term:
        query = query.filter(Legislator.reele_gbn_nm == term)
    
    # 기본 정렬 (이름 오름차순)
    query = query.order_by(Legislator.hg_nm)
    
    # 쿼리 실행
    legislators = query.all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "tier": legislator.tier
        })
    
    return result

def get_legislator_detail(db: Session, legislator_id: int) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 의원 상세 정보 조회
    # 반환: 의원 상세 정보
    pass

def get_legislator_stats(db: Session, legislator_id: int) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 의원 스탯 정보 조회
    # 반환: 의원 스탯 정보
    pass

def get_legislator_basic_info(db: Session, legislator_id: int) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 의원 기본 정보 조회
    # 반환: 의원 기본 정보
    pass

def get_legislator_sns(db: Session, legislator_id: int) -> Dict[str, Any]:
    # 호출: db.query(LegislatorSNS)로 특정 의원 SNS 정보 조회
    # 반환: 의원 SNS 정보
    pass

def get_legislator_committee_history(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(CommitteeHistory)로 특정 의원 위원회 경력 조회
    # 반환: 의원 위원회 경력
    pass