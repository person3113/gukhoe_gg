from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os

from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory
from app.utils.image_path_helper import ImagePathHelper

def get_filter_options(db: Session) -> Dict[str, List[str]]:
    """
    필터 옵션(정당, 위원회, 초선/재선, 선거구) 데이터 조회
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        필터 옵션 딕셔너리
    """
    # 정당 목록 조회
    parties = db.query(Legislator.poly_nm).distinct().all()
    party_list = [party[0] for party in parties if party[0]]
    
    # 위원회 목록 조회 - 상임위원회와 상설특별위원회만 필터링
    committees = db.query(Committee.dept_nm).filter(
        (Committee.cmt_div_nm.like('%상임위원회%')) | 
        (Committee.cmt_div_nm.like('%상설특별위원회%'))
    ).distinct().all()
    committee_list = [committee[0] for committee in committees if committee[0]]
    
    # 초선/재선 목록 조회
    terms = db.query(Legislator.reele_gbn_nm).distinct().all()
    term_list = [term[0] for term in terms if term[0]]
    
    # 초선/재선 목록 정렬 (숫자 추출 후 정렬)
    def term_sort_key(term):
        # "초선", "재선", "3선", "4선", "5선" 등의 형태에서 숫자를 추출
        if term == "초선":
            return 1
        elif term == "재선":
            return 2
        else:
            # "3선", "4선", "5선" 등에서 숫자만 추출
            for char in term:
                if char.isdigit():
                    return int(char)
            return 999  # 숫자를 찾지 못한 경우 큰 숫자 반환
    
    term_list.sort(key=term_sort_key)
    
    # 선거구 정보 수집 - 광역시/도 단위와 의원 수 함께 계산
    district_counts = {}
    legislators = db.query(Legislator).all()
    
    for legislator in legislators:
        district = legislator.orig_nm
        if not district:
            continue
            
        # 세종특별자치시는 '기타'로 분류
        if district.startswith('세종특별자치시'):
            region = '기타'
        elif ' ' in district:
            region = district.split(' ')[0]  # 첫 번째 공백을 기준으로 광역시/도 추출
        else:
            region = district  # '비례대표'와 같이 공백이 없는 경우
            
        # 지역별 의원 수 카운트
        if region in district_counts:
            district_counts[region] += 1
        else:
            district_counts[region] = 1
    
    # 의원 수 기준으로 내림차순 정렬
    district_list = sorted(district_counts.keys(), key=lambda x: district_counts[x], reverse=True)
    
    # 필터 옵션 딕셔너리 생성
    filter_options = {
        "parties": party_list,
        "committees": committee_list,
        "terms": term_list,
        "districts": district_list
    }
    
    return filter_options

def _get_optimized_image_url(profile_image_url: str, image_type: str = "list") -> str:
    """
    최적화된 이미지 URL 생성
    
    Args:
        profile_image_url: 원본 이미지 URL
        image_type: 이미지 유형 (detail, list, thumb)
    
    Returns:
        최적화된 이미지 URL
    """
    if not profile_image_url or profile_image_url.startswith('http'):
        return profile_image_url or "/static/images/legislators/default.png"
    
    # 파일명만 추출
    filename = profile_image_url.split('/')[-1]
    
    # ImagePathHelper를 사용하여 최적화된 이미지 경로 반환
    return ImagePathHelper.get_optimized_image_path(filename, image_type)

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
        if district == '기타':
            # '기타' 카테고리는 세종특별자치시 선거구를 포함
            query = query.filter(Legislator.orig_nm.like('세종특별자치시%'))
        else:
            # 광역시/도 단위로 선택한 경우, 해당 지역으로 시작하는 모든 선거구 포함
            query = query.filter(Legislator.orig_nm.like(f'{district}%'))
    
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
            "profile_image_url": _get_optimized_image_url(legislator.profile_image_url),
            "tier": legislator.tier
        })
    
    return result

def get_legislators_list(
    db: Session, 
    name: Optional[str] = None,
    party: Optional[str] = None,
    district: Optional[str] = None,
    term: Optional[str] = None
) -> List[Dict]:
    """
    국회의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        name: 의원명 필터
        party: 정당 필터
        district: 선거구 필터
        term: 당선 횟수 필터
    
    Returns:
        국회의원 목록
    """
    query = db.query(Legislator)
    
    # 필터링 적용
    if name:
        query = query.filter(Legislator.hg_nm.contains(name))
    if party:
        query = query.filter(Legislator.poly_nm == party)
    if district:
        query = query.filter(Legislator.orig_nm == district)
    if term:
        query = query.filter(Legislator.reele_gbn_nm == term)
    
    legislators = query.all()
    
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "profile_image_url": _get_optimized_image_url(legislator.profile_image_url, "list")
        })
    
    return result

def get_legislator_detail(db: Session, legislator_id: int) -> Optional[Dict]:
    """
    국회의원 상세 정보 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        국회의원 상세 정보
    """
    legislator = db.query(Legislator).filter(Legislator.id == legislator_id).first()
    
    if not legislator:
        return None
    
    # 스탯 계산
    overall_rank = db.query(Legislator).filter(
        Legislator.overall_score >= legislator.overall_score
    ).count()
    
    result = {
        "id": legislator.id,
        "name": legislator.hg_nm,
        "eng_name": legislator.eng_nm,
        "profile_image_url": _get_optimized_image_url(legislator.profile_image_url, "detail"),
        "party": legislator.poly_nm,
        "district": legislator.orig_nm,
        "term": legislator.reele_gbn_nm,
        "committee": legislator.cmit_nm,
        "gender": legislator.sex_gbn_nm,
        "birth_date": legislator.bth_date,
        "tel": legislator.tel_no,
        "email": legislator.e_mail,
        "profile": legislator.mem_title,
        "tier": legislator.tier,
        "overall_rank": overall_rank,
        "overall_score": legislator.overall_score,
        "participation_score": legislator.participation_score,
        "legislation_score": legislator.legislation_score,
        "speech_score": legislator.speech_score,
        "voting_score": legislator.voting_score,
        "cooperation_score": legislator.cooperation_score
    }
    
    return result

def get_legislator_stats(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원의 스탯 정보 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        의원 스탯 정보 딕셔너리
    """
    # 의원 정보 조회
    legislator = db.query(Legislator).filter(Legislator.id == legislator_id).first()
    
    if not legislator:
        return None
    
    # 스탯 정보 추출
    result = {
        "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
        "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
        "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
        "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
        "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
        "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
    }
    
    return result

def get_legislator_sns(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원의 SNS 정보 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        의원 SNS 정보 딕셔너리
    """
    # SNS 정보 조회
    sns = db.query(LegislatorSNS).filter(LegislatorSNS.legislator_id == legislator_id).first()
    
    if not sns:
        return {
            "twitter_url": None,
            "facebook_url": None,
            "youtube_url": None,
            "blog_url": None,
        }
    
    # SNS 정보 딕셔너리 변환
    result = {
        "twitter_url": sns.twitter_url,
        "facebook_url": sns.facebook_url,
        "youtube_url": sns.youtube_url,
        "blog_url": sns.blog_url,
    }
    
    return result

def get_legislator_committee_history(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    """
    특정 의원의 위원회 경력 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        의원 위원회 경력 목록
    """
    # 위원회 경력 조회
    histories = db.query(CommitteeHistory).filter(CommitteeHistory.legislator_id == legislator_id).all()
    
    # 위원회 경력 딕셔너리 변환
    result = []
    for history in histories:
        result.append({
            "committee_name": history.profile_sj,
            "position": history.frto_date,
        })
    
    return result
