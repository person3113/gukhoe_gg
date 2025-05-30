from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional, Tuple

from app.models.bill import Bill
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeMember
from app.utils.image_path_helper import ImagePathHelper

def get_average_stats(db: Session) -> Dict[str, Any]:
    """
    모든 의원의 평균 스탯 계산
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        평균 스탯 딕셔너리
    """
    # 각 스탯별 평균 계산
    result = db.query(
        func.avg(Legislator.participation_score).label("participation_score"),
        func.avg(Legislator.legislation_score).label("legislation_score"),
        func.avg(Legislator.speech_score).label("speech_score"),
        func.avg(Legislator.voting_score).label("voting_score"),
        func.avg(Legislator.cooperation_score).label("cooperation_score"),
        func.avg(Legislator.overall_score).label("overall_score")
    ).first()
    
    # 딕셔너리로 변환 및 반올림
    avg_stats = {
        "participation_score": round(result.participation_score, 1) if result.participation_score else 0,
        "legislation_score": round(result.legislation_score, 1) if result.legislation_score else 0,
        "speech_score": round(result.speech_score, 1) if result.speech_score else 0,
        "voting_score": round(result.voting_score, 1) if result.voting_score else 0,
        "cooperation_score": round(result.cooperation_score, 1) if result.cooperation_score else 0,
        "overall_score": round(result.overall_score, 1) if result.overall_score else 0,
    }
    
    return avg_stats

### 잡다한 랭킹 - 홈 ###
def get_party_average_stats(db: Session, stat: str = 'asset') -> Dict[str, Any]:
    """
    정당별 특정 통계의 평균값 계산
    
    Args:
        db: 데이터베이스 세션
        stat: 계산할 통계 항목 (기본값: 'asset')
    
    Returns:
        정당별 평균 통계 딕셔너리
    """
    # 정당 목록 조회
    party_query = db.query(Legislator.poly_nm).distinct().all()
    parties = [party[0] for party in party_query if party[0]]
    
    # 정당별 평균 통계 계산
    result = {}
    for party in parties:
        # 통계 항목에 따라 다른 컬럼 선택
        if stat == 'asset':
            avg_value = db.query(func.avg(Legislator.asset)).filter(
                Legislator.poly_nm == party,
                Legislator.hg_nm != '백선희'  # 백선희 의원 제외
            ).scalar()
            # 재산은 억 단위로 표시 (10^8으로 나눔)
            avg_value = round(avg_value / 100000000, 1) if avg_value else 0
        elif stat == 'overall_score':
            avg_value = db.query(func.avg(Legislator.overall_score)).filter(
                Legislator.poly_nm == party
            ).scalar()
            avg_value = round(avg_value, 1) if avg_value else 0
        elif stat == 'participation_score':
            avg_value = db.query(func.avg(Legislator.participation_score)).filter(
                Legislator.poly_nm == party
            ).scalar()
            avg_value = round(avg_value, 1) if avg_value else 0
        elif stat == 'legislation_score':
            avg_value = db.query(func.avg(Legislator.legislation_score)).filter(
                Legislator.poly_nm == party
            ).scalar()
            avg_value = round(avg_value, 1) if avg_value else 0
        else:
            avg_value = 0
        
        result[party] = avg_value
    
    return result

def get_term_average_stats(db: Session, stat: str = 'overall_score') -> Dict[str, Any]:
    """
    초선/재선별 특정 통계의 평균값 계산
    
    Args:
        db: 데이터베이스 세션
        stat: 계산할 통계 항목 (기본값: 'overall_score')
    
    Returns:
        초선/재선별 평균 통계 딕셔너리
    """
    # 초선/재선 구분 목록 조회
    term_query = db.query(Legislator.reele_gbn_nm).distinct().all()
    terms = [term[0] for term in term_query if term[0]]
    
    # 초선/재선별 순서 정렬
    def term_sort_key(term):
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
    
    terms.sort(key=term_sort_key)
    
    # 초선/재선별 평균 통계 계산
    result = {}
    for term in terms:
        # 통계 항목에 따라 다른 컬럼 선택
        if stat == 'overall_score':
            avg_value = db.query(func.avg(Legislator.overall_score)).filter(
                Legislator.reele_gbn_nm == term
            ).scalar()
        elif stat == 'asset':
            avg_value = db.query(func.avg(Legislator.asset)).filter(
                Legislator.reele_gbn_nm == term,
                Legislator.hg_nm != '백선희'  # 백선희 의원 제외
            ).scalar()
            # 재산은 억 단위로 표시 (10^8으로 나눔)
            avg_value = round(avg_value / 100000000, 1) if avg_value else 0
            return result
        elif stat == 'participation_score':
            avg_value = db.query(func.avg(Legislator.participation_score)).filter(
                Legislator.reele_gbn_nm == term
            ).scalar()
        elif stat == 'legislation_score':
            avg_value = db.query(func.avg(Legislator.legislation_score)).filter(
                Legislator.reele_gbn_nm == term
            ).scalar()
        else:
            avg_value = 0
            
        result[term] = round(avg_value, 1) if avg_value else 0
    
    return result

### 잡다한 랭킹 - 정당 ###
def get_party_average_scores(db: Session) -> Dict[str, float]:
    """
    정당별 평균 종합점수 조회 (의원 수 기준 정렬)
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        정당별 평균 종합점수 딕셔너리 (의원 수 기준 정렬)
    """
    # 정당별 의원 수 조회 및 내림차순 정렬
    party_counts = db.query(
        Legislator.poly_nm, 
        func.count(Legislator.id).label('count')
    ).group_by(
        Legislator.poly_nm
    ).order_by(  # 이 부분이 빠져있었습니다!
        func.count(Legislator.id).desc()
    ).all()
    
    # 의원 수 기준으로 정렬된 정당 목록 생성
    party_list = [party[0] for party in party_counts if party[0]]
    
    # 정당별 평균 종합점수 계산
    result = {}
    for party in party_list:
        # 해당 정당 의원들의 평균 종합점수 계산
        avg_score = db.query(func.avg(Legislator.overall_score)).filter(
            Legislator.poly_nm == party
        ).scalar()
        
        # 결과 딕셔너리에 추가 (None인 경우 0으로 처리)
        result[party] = round(avg_score, 1) if avg_score else 0
    
    return result

def get_party_average_bill_counts(db: Session) -> Dict[str, float]:
    """
    정당별 평균 대표발의안수 조회 (의원 수 기준 정렬)
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        정당별 평균 대표발의안수 딕셔너리 (의원 수 기준 정렬)
    """
    # 정당별 의원 수 조회
    party_counts = db.query(
        Legislator.poly_nm, 
        func.count(Legislator.id).label('count')
    ).group_by(
        Legislator.poly_nm
    ).order_by(
        func.count(Legislator.id).desc()
    ).all()
    
    # 의원 수 기준으로 정렬된 정당 목록 생성
    party_list = [party[0] for party in party_counts if party[0]]
    
    # 정당별 평균 대표발의안수 계산
    result = {}
    for party in party_list:
        # 해당 정당 의원들의 ID 목록
        legislator_ids = db.query(Legislator.id).filter(
            Legislator.poly_nm == party
        ).all()
        legislator_ids = [id[0] for id in legislator_ids]
        
        if not legislator_ids:
            result[party] = 0
            continue
        
        # 각 의원별 대표발의안수 계산
        bill_counts = []
        for legislator_id in legislator_ids:
            count = db.query(func.count(Bill.id)).filter(
                Bill.main_proposer_id == legislator_id
            ).scalar()
            bill_counts.append(count)
        
        # 평균 계산
        avg_count = sum(bill_counts) / len(legislator_ids) if legislator_ids else 0
        result[party] = round(avg_count, 1)
    
    return result

def get_party_stats_summary(db: Session, party_name: str) -> Dict[str, Any]:
    """
    특정 정당의 통계 요약 정보 조회
    
    Args:
        db: 데이터베이스 세션
        party_name: 정당명
    
    Returns:
        정당 통계 요약 딕셔너리
    """
    # 해당 정당 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min")
    ).filter(
        Legislator.poly_nm == party_name
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier, 
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.poly_nm == party_name
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislators_by_party(db: Session, party_name: str) -> List[Dict[str, Any]]:
    """
    특정 정당 소속 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        party_name: 정당명
    
    Returns:
        의원 목록 (종합점수 내림차순 정렬)
    """
    # 특정 정당 소속 의원 조회 (종합점수 내림차순 정렬)
    legislators = db.query(Legislator).filter(
        Legislator.poly_nm == party_name
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

### 잡다한 랭킹 - 위원회 ###
def get_committee_processing_ratio(db: Session) -> Dict[str, Any]:
    """
    위원회별 법안 처리 비율 계산
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        위원회별 처리 비율 딕셔너리
    """
    # 위원회 목록 조회
    committees = db.query(Committee).all()
    
    # 위원회별 처리 비율 계산
    result = {}
    for committee in committees:
        # 접수 건수가 0인 경우 처리 비율은 0%로 설정
        if committee.rcp_cnt and committee.rcp_cnt > 0:
            ratio = (committee.proc_cnt / committee.rcp_cnt) * 100
        else:
            ratio = 0
            
        result[committee.dept_nm] = {
            "name": committee.dept_nm,
            "reception_count": committee.rcp_cnt,
            "processed_count": committee.proc_cnt,
            "ratio": round(ratio, 1)
        }
    
    return result

def get_committee_average_scores(db: Session) -> Dict[str, float]:
    """
    위원회별 평균 종합점수 계산
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        위원회별 평균 종합점수 딕셔너리
    """
    # 위원회 목록 조회
    committees = db.query(Committee).all()
    
    # 위원회별 평균 종합점수 계산
    result = {}
    for committee in committees:
        # 해당 위원회 소속 의원들의 ID 조회
        member_ids = db.query(CommitteeMember.legislator_id).filter(
            CommitteeMember.committee_id == committee.id
        ).all()
        member_ids = [mid[0] for mid in member_ids]
        
        if not member_ids:
            result[committee.dept_nm] = 0
            continue
        
        # 해당 위원회 소속 의원들의 평균 종합점수 계산
        avg_score = db.query(func.avg(Legislator.overall_score)).filter(
            Legislator.id.in_(member_ids)
        ).scalar()
        
        result[committee.dept_nm] = round(avg_score, 1) if avg_score else 0
    
    return result

def get_committee_stats_summary(db: Session, committee_name: str) -> Dict[str, Any]:
    """
    특정 위원회의 통계 요약 정보 조회
    
    Args:
        db: 데이터베이스 세션
        committee_name: 위원회명
        
    Returns:
        위원회 통계 요약 딕셔너리
    """
    # 위원회 정보 조회
    committee = db.query(Committee).filter(Committee.dept_nm == committee_name).first()
    
    if not committee:
        return {
            "avg": 0,
            "max": 0,
            "min": 0,
            "tier_distribution": {},
            "member_count": 0,
            "processing_ratio": 0
        }
    
    # 위원회 소속 의원 ID 목록 조회
    member_ids = db.query(CommitteeMember.legislator_id).filter(
        CommitteeMember.committee_id == committee.id
    ).all()
    member_ids = [mid[0] for mid in member_ids]
    
    # 의원 수가 0인 경우
    if not member_ids:
        return {
            "avg": 0,
            "max": 0,
            "min": 0,
            "tier_distribution": {},
            "member_count": 0,
            "processing_ratio": 0 if not committee.rcp_cnt else round((committee.proc_cnt / committee.rcp_cnt) * 100, 1)
        }
    
    # 위원회 소속 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min")
    ).filter(
        Legislator.id.in_(member_ids)
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.id.in_(member_ids)
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 처리 비율 계산
    processing_ratio = 0
    if committee.rcp_cnt and committee.rcp_cnt > 0:
        processing_ratio = (committee.proc_cnt / committee.rcp_cnt) * 100
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "tier_distribution": tier_distribution,
        "member_count": len(member_ids),
        "processing_ratio": round(processing_ratio, 1)
    }
    
    return result

def get_legislators_by_committee(db: Session, committee_name: str) -> List[Dict[str, Any]]:
    """
    특정 위원회 소속 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        committee_name: 위원회명
    
    Returns:
        의원 목록 (종합점수 내림차순 정렬)
    """
    # 위원회 ID 조회
    committee = db.query(Committee).filter(Committee.dept_nm == committee_name).first()
    if not committee:
        return []
    
    # 해당 위원회에 속한 의원 ID 목록 조회
    member_ids = db.query(CommitteeMember.legislator_id).filter(
        CommitteeMember.committee_id == committee.id
    ).all()
    
    # ID 목록 변환
    legislator_ids = [member_id[0] for member_id in member_ids]
    
    # 의원 정보 조회 (종합점수 내림차순 정렬)
    legislators = db.query(Legislator).filter(
        Legislator.id.in_(legislator_ids)
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

### 잡다한 랭킹 - 초선/재선 ###
def get_tier_distribution_by_term(db: Session) -> Dict[str, Dict[str, int]]:
    """
    초선/재선별 티어 분포 계산
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        초선/재선별 티어 분포 딕셔너리
    """
    # 초선/재선 구분 목록 조회
    term_query = db.query(Legislator.reele_gbn_nm).distinct().all()
    terms = [term[0] for term in term_query if term[0]]
    
    # 순서 정렬 - 선수에 따라 정렬
    def term_sort_key(term):
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
    
    terms.sort(key=term_sort_key)
    
    # 초선/재선별 티어 분포 계산
    result = {}
    for term in terms:
        # 해당 선수 의원들의 티어 분포 조회
        tier_distribution = db.query(
            Legislator.tier, func.count(Legislator.id).label('count')
        ).filter(
            Legislator.reele_gbn_nm == term
        ).group_by(
            Legislator.tier
        ).all()
        
        # 결과 딕셔너리 구성
        term_result = {}
        for tier, count in tier_distribution:
            term_result[tier] = count
            
        result[term] = term_result
    
    return result

def get_term_average_assets(db: Session) -> Dict[str, float]:
    """
    초선/재선별 평균 재산 계산
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        초선/재선별 평균 재산 딕셔너리
    """
    # 초선/재선 구분 목록 조회
    term_query = db.query(Legislator.reele_gbn_nm).distinct().all()
    terms = [term[0] for term in term_query if term[0]]
    
    # 초선/재선별 순서 정렬
    def term_sort_key(term):
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
    
    terms.sort(key=term_sort_key)
    
    # 초선/재선별 평균 재산 계산
    result = {}
    for term in terms:
        # 해당 선수 의원들의 평균 재산 계산
        avg_asset = db.query(func.avg(Legislator.asset)).filter(
            Legislator.reele_gbn_nm == term,
            Legislator.hg_nm != '백선희'  # 백선희 의원 제외
        ).scalar()
        
        # 억 단위로 변환
        result[term] = round(avg_asset / 100000000, 1) if avg_asset else 0
    
    return result

def get_term_stats_summary(db: Session, term: str) -> Dict[str, Any]:
    """
    특정 선수(초선/재선 등) 의원들의 통계 요약 계산
    
    Args:
        db: 데이터베이스 세션
        term: 선수 구분 (초선, 재선 등)
        
    Returns:
        선수별 통계 요약 딕셔너리
    """
    # 해당 선수 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min"),
        func.avg(Legislator.asset).label("avg_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.reele_gbn_nm == term
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.reele_gbn_nm == term
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "avg_asset": round(stats.avg_asset / 100000000, 1) if stats.avg_asset else 0,  # 억 단위
        "count": stats.count,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislators_by_term(db: Session, term: str) -> List[Dict[str, Any]]:
    """
    특정 선수 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        term: 선수 구분 (초선, 재선, 3선 등)
    
    Returns:
        의원 목록 (종합점수 내림차순 정렬)
    """
    # 특정 선수 의원 조회 (종합점수 내림차순 정렬)
    legislators = db.query(Legislator).filter(
        Legislator.reele_gbn_nm == term
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

def get_tier_distribution_by_gender(db: Session) -> Dict[str, Dict[str, int]]:
    """
    성별 티어 분포 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        성별 티어 분포 딕셔너리
    """
    # 성별 목록 조회
    gender_query = db.query(Legislator.sex_gbn_nm).distinct().all()
    genders = [gender[0] for gender in gender_query if gender[0]]
    
    # 성별 티어 분포 계산
    result = {}
    for gender in genders:
        # 해당 성별 의원들의 티어 분포 조회
        tier_distribution = db.query(
            Legislator.tier,
            func.count(Legislator.id).label("count")
        ).filter(
            Legislator.sex_gbn_nm == gender
        ).group_by(
            Legislator.tier
        ).all()
        
        # 결과 딕셔너리 구성
        gender_result = {}
        for tier, count in tier_distribution:
            gender_result[tier] = count
            
        result[gender] = gender_result
    
    return result

def get_gender_average_assets(db: Session) -> Dict[str, float]:
    """
    성별 평균 재산 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        성별 평균 재산 딕셔너리
    """
    # 성별 목록 조회
    gender_query = db.query(Legislator.sex_gbn_nm).distinct().all()
    genders = [gender[0] for gender in gender_query if gender[0]]
    
    # 성별 평균 재산 계산
    result = {}
    for gender in genders:
        # 해당 성별 의원들의 평균 재산 계산
        avg_asset = db.query(func.avg(Legislator.asset)).filter(
            Legislator.sex_gbn_nm == gender,
            Legislator.hg_nm != '백선희'  # 백선희 의원 제외
        ).scalar()
        
        result[gender] = round(avg_asset / 100000000, 1) if avg_asset else 0
    
    return result

def get_gender_stats_summary(db: Session, gender: str) -> Dict[str, Any]:
    """
    특정 성별 의원들의 통계 요약 계산
    
    Args:
        db: 데이터베이스 세션
        gender: 성별
        
    Returns:
        성별 통계 요약 딕셔너리
    """
    # 해당 성별 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min"),
        func.avg(Legislator.asset).label("avg_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.sex_gbn_nm == gender
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.sex_gbn_nm == gender
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "avg_asset": round(stats.avg_asset / 100000000, 1) if stats.avg_asset else 0,  # 억 단위
        "count": stats.count,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislator_asset_details(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원의 재산 상세 정보 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 의원 ID
        gender: 성별
        
    Returns:
        성별 통계 요약 딕셔너리
    """
    # 해당 성별 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min"),
        func.avg(Legislator.asset).label("avg_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.sex_gbn_nm == gender
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.sex_gbn_nm == gender
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "avg_asset": round(stats.avg_asset / 100000000, 1) if stats.avg_asset else 0,  # 억 단위
        "count": stats.count,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislators_by_gender(db: Session, gender: str) -> List[Dict[str, Any]]:
    """
    특정 성별 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        gender: 성별
    
    Returns:
        의원 목록 (종합점수 내림차순 정렬)
    """
    # 특정 성별 의원 조회 (종합점수 내림차순 정렬)
    legislators = db.query(Legislator).filter(
        Legislator.sex_gbn_nm == gender
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

def get_age_average_scores(db: Session) -> Dict[str, float]:
    """
    나이대별 평균 종합점수 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        나이대별 평균 종합점수 딕셔너리
    """
    # 현재 연도 (2025년)
    current_year = 2025
    
    # 나이대 구분 (30대, 40대, 50대, 60대, 70대 이상)
    age_groups = {
        "30대 이하": (current_year - 39, current_year),
        "40대": (current_year - 49, current_year - 40),
        "50대": (current_year - 59, current_year - 50),
        "60대": (current_year - 69, current_year - 60),
        "70대 이상": (0, current_year - 70)
    }
    
    # 나이대별 평균 종합점수 계산
    result = {}
    for group, (min_year, max_year) in age_groups.items():
        # 해당 나이대 의원들의 평균 종합점수 계산
        avg_score = db.query(func.avg(Legislator.overall_score)).filter(
            Legislator.bth_date.between(str(min_year), str(max_year))
        ).scalar()
        
        result[group] = round(avg_score, 1) if avg_score else 0
    
    return result

def get_age_average_assets(db: Session) -> Dict[str, float]:
    """
    나이대별 평균 재산 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        나이대별 평균 재산 딕셔너리
    """
    # 현재 연도 (2025년)
    current_year = 2025
    
    # 나이대 구분 (30대, 40대, 50대, 60대, 70대 이상)
    age_groups = {
        "30대 이하": (current_year - 39, current_year),
        "40대": (current_year - 49, current_year - 40),
        "50대": (current_year - 59, current_year - 50),
        "60대": (current_year - 69, current_year - 60),
        "70대 이상": (0, current_year - 70)
    }
    
    # 나이대별 평균 재산 계산
    result = {}
    for group, (min_year, max_year) in age_groups.items():
        # 해당 나이대 의원들의 평균 재산 계산
        avg_asset = db.query(func.avg(Legislator.asset)).filter(
            Legislator.bth_date.between(str(min_year), str(max_year)),
            Legislator.hg_nm != '백선희'  # 백선희 의원 제외
        ).scalar()
        
        # 억 단위로 변환
        result[group] = round(avg_asset / 100000000, 1) if avg_asset else 0
    
    return result

def get_age_stats_summary(db: Session, age_group: str) -> Dict[str, Any]:
    """
    특정 나이대 의원들의 통계 요약 계산
    
    Args:
        db: 데이터베이스 세션
        age_group: 나이대 ('30대 이하', '40대', '50대', '60대', '70대 이상')
        
    Returns:
        나이대별 통계 요약 딕셔너리
    """
    # 현재 연도 (2025년)
    current_year = 2025
    
    # 나이대에 따른 출생연도 범위 설정
    if age_group == "30대 이하":
        birth_year_min, birth_year_max = current_year - 39, current_year
    elif age_group == "40대":
        birth_year_min, birth_year_max = current_year - 49, current_year - 40
    elif age_group == "50대":
        birth_year_min, birth_year_max = current_year - 59, current_year - 50
    elif age_group == "60대":
        birth_year_min, birth_year_max = current_year - 69, current_year - 60
    elif age_group == "70대 이상":
        birth_year_min, birth_year_max = 0, current_year - 70
    else:
        return {
            "avg": 0,
            "max": 0,
            "min": 0,
            "avg_asset": 0,
            "count": 0,
            "tier_distribution": {}
        }
    
    # 해당 나이대 의원들의 점수 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg"),
        func.max(Legislator.overall_score).label("max"),
        func.min(Legislator.overall_score).label("min"),
        func.avg(Legislator.asset).label("avg_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.bth_date.between(str(birth_year_min), str(birth_year_max))
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.bth_date.between(str(birth_year_min), str(birth_year_max))
    ).group_by(
        Legislator.tier
    ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg": round(stats.avg, 1) if stats.avg else 0,
        "max": round(stats.max, 1) if stats.max else 0,
        "min": round(stats.min, 1) if stats.min else 0,
        "avg_asset": round(stats.avg_asset / 100000000, 1) if stats.avg_asset else 0,  # 억 단위
        "count": stats.count or 0,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislators_by_age_group(db: Session, age_group: str) -> List[Dict[str, Any]]:
    """
    특정 연령대 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        age_group: 연령대 (20대, 30대, 40대, 50대, 60대, 70대 이상)
    
    Returns:
        의원 목록 (종합점수 내림차순 정렬)
    """
    # 연령대별 출생연도 범위 계산
    import datetime
    current_year = datetime.datetime.now().year
    
    # 연령대별 출생년도 범위 계산 (각 세대의 시작 나이와 끝 나이를 출생년도로 변환)
    age_ranges = {
        "20대": (current_year - 29, current_year - 20),  # 20~29세
        "30대": (current_year - 39, current_year - 30),  # 30~39세
        "40대": (current_year - 49, current_year - 40),  # 40~49세
        "50대": (current_year - 59, current_year - 50),  # 50~59세
        "60대": (current_year - 69, current_year - 60),  # 60~69세
        "70대 이상": (current_year - 100, current_year - 70)  # 70세 이상
    }
    
    # 해당 연령대가 유효한지 확인
    if age_group not in age_ranges:
        return []
    
    # 출생년도 범위
    min_birth_year, max_birth_year = age_ranges[age_group]
    
    # 연령대에 해당하는 의원 목록 조회
    legislators = []
    all_legislators = db.query(Legislator).order_by(Legislator.overall_score.desc()).all()
    
    for legislator in all_legislators:
        # 생년월일에서 출생년도 추출
        birth_date = legislator.bth_date
        if not birth_date:
            continue
            
        try:
            # 생년월일 문자열에서 출생년도 추출 (YYYYMMDD 형식)
            birth_year = int(birth_date[:4])
            
            # 연령대 범위에 포함되는지 확인
            if min_birth_year <= birth_year <= max_birth_year:
                legislators.append(legislator)
        except (ValueError, IndexError):
            # 생년월일 형식이 잘못된 경우 무시
            continue
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0
        })
    
    return result

def get_score_asset_correlation(db: Session, for_chart: bool = False) -> Dict[str, Any]:
    """
    활동점수와 재산의 상관관계 데이터 계산
    
    Args:
        db: 데이터베이스 세션
        for_chart: 차트용 데이터인지 여부. True이면 일부 의원만 선택하여 그래프가 고르게 보이도록 함.
        
    Returns:
        상관관계 데이터 딕셔너리
    """
    # 의원별 점수와 재산 데이터 조회 (백선희 의원 제외)
    legislators = db.query(
        Legislator.id,
        Legislator.hg_nm,
        Legislator.overall_score,
        Legislator.asset
    ).filter(
        Legislator.hg_nm != '백선희',  # 백선희 의원 제외
        Legislator.overall_score.isnot(None),
        Legislator.asset.isnot(None)
    ).all()
    
    # 의원 데이터를 딕셔너리 리스트로 변환
    leg_data = []
    for leg in legislators:
        leg_data.append({
            "id": leg.id,
            "name": leg.hg_nm,
            "score": leg.overall_score,
            "asset": leg.asset,
            "asset_billion": leg.asset / 100000000  # 억 단위
        })
    
    # 재산 기준 정렬
    leg_data.sort(key=lambda x: x["asset_billion"])
    
    # 재산 기준 그룹화
    total_legs = len(leg_data)
    
    # 극단적인 재산 값을 가진 의원들 제외 (90 퍼센타일 초과 재산)
    asset_cutoff_index = int(total_legs * 0.9)  # 90% 퍼센타일
    if asset_cutoff_index < total_legs:
        asset_cutoff = leg_data[asset_cutoff_index]["asset_billion"]
    else:
        asset_cutoff = float('inf')
    
    # 점수 기준 정렬
    leg_data.sort(key=lambda x: x["score"])
    
    # 점수 범위 계산
    score_min = min([leg["score"] for leg in leg_data])
    score_max = max([leg["score"] for leg in leg_data])
    
    # 차트용이 아니면 모든 의원 데이터 반환
    if not for_chart:
        data_points = []
        for leg in leg_data:
            data_points.append({
                "id": leg["id"],
                "name": leg["name"],
                "score": round(leg["score"], 1),
                "asset": round(leg["asset_billion"], 1)  # 억 단위
            })
    else:
        # 차트용이면 일부 의원만 선택하여 그래프가 고르게 보이도록 함
        # 점수 범위를 등간격으로 분할
        num_score_bins = 10
        score_bin_size = (score_max - score_min) / num_score_bins
        score_bins = {}
        
        # 각 점수 구간별 의원 분류
        for i in range(num_score_bins):
            bin_min = score_min + i * score_bin_size
            bin_max = score_min + (i + 1) * score_bin_size
            score_bins[i] = []
            
            for leg in leg_data:
                # 극단적인 재산 값을 가진 의원 제외
                if leg["asset_billion"] > asset_cutoff:
                    continue
                    
                if i < num_score_bins - 1:
                    if bin_min <= leg["score"] < bin_max:
                        score_bins[i].append(leg)
                else:  # 마지막 구간은 마지막 값 포함
                    if bin_min <= leg["score"] <= bin_max:
                        score_bins[i].append(leg)
        
        # 데이터 포인트 생성
        data_points = []
        
        # 각 점수 구간에서 재산 범위별 의원 선택
        for bin_idx, bin_legs in score_bins.items():
            if not bin_legs:
                continue
                
            # 재산 기준 정렬
            bin_legs.sort(key=lambda x: x["asset_billion"])
            
            # 각 구간에서 재산 범위별로 고르게 샘플링
            if len(bin_legs) >= 5:
                # 최소, 25%, 50%, 75%, 최대 재산 의원 선택
                sample_indices = [
                    0,  # 최소 재산
                    len(bin_legs) // 4,  # 25%
                    len(bin_legs) // 2,  # 50%
                    3 * len(bin_legs) // 4,  # 75%
                    len(bin_legs) - 1  # 최대 재산
                ]
                samples = [bin_legs[i] for i in sample_indices]
            else:
                # 구간에 의원이 적으면 모두 포함
                samples = bin_legs
            
            # 샘플링된 의원들을 데이터 포인트로 추가
            for legislator in samples:
                data_points.append({
                    "id": legislator["id"],
                    "name": legislator["name"],
                    "score": round(legislator["score"], 1),
                    "asset": round(legislator["asset_billion"], 1)  # 억 단위
                })
    
    # 결과 구성
    result = {
        "data_points": data_points
    }
    
    return result

def get_party_asset_ratio(db: Session) -> Dict[str, Any]:
    """
    정당별 재산 비율 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        정당별 재산 비율 딕셔너리
    """
    # 전체 재산 합계 조회 (백선희 의원 제외)
    total_asset = db.query(func.sum(Legislator.asset)).filter(
        Legislator.hg_nm != '백선희'  # 백선희 의원 제외
    ).scalar() or 1  # 0으로 나누기 방지
    
    # 정당별 재산 합계 조회 (백선희 의원 제외)
    party_assets = db.query(
        Legislator.poly_nm,
        func.sum(Legislator.asset).label("total_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.hg_nm != '백선희'  # 백선희 의원 제외
    ).group_by(
        Legislator.poly_nm
    ).all()
    
    # 결과 구성
    result = {}
    for party, asset, count in party_assets:
        if party and asset is not None:  # None이 아닌 경우만 처리
            ratio = (asset / total_asset) * 100
            result[party] = {
                "total_asset": round(asset / 100000000, 1),  # 억 단위
                "ratio": round(ratio, 1),
                "count": count
            }
    
    return result

def get_asset_percentile_ranges(db: Session) -> Dict[str, Tuple[int, int]]:
    """
    자산 백분위 범위 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        백분위 구간별 자산 범위 딕셔너리
    """
    # 백선희 의원 제외하고 모든 의원의 자산 조회
    assets = db.query(Legislator.asset).filter(
        Legislator.hg_nm != '백선희'  # 백선희 의원 제외
    ).order_by(
        Legislator.asset
    ).all()
    
    assets = [asset[0] for asset in assets]
    total_count = len(assets)
    
    if total_count == 0:
        return {}
    
    # 각 구간이 정확히 60명씩 포함되도록 인덱스 설정
    # 총 300명이므로 0-59, 60-119, 120-179, 180-239, 240-299로 나눔
    
    # 백분위 계산 - 구간이 겹치지 않도록 조정
    percentile_ranges = {
        "0-20 백분위": (assets[0], assets[59]),
        "20-40 백분위": (assets[59] + 1, assets[119]),
        "40-60 백분위": (assets[119] + 1, assets[179]),
        "60-80 백분위": (assets[179] + 1, assets[239]),
        "80-100 백분위": (assets[239] + 1, assets[total_count - 1])
    }
    
    return percentile_ranges

def get_asset_stats_summary(db: Session, asset_group: str) -> Dict[str, Any]:
    """
    특정 재산 구간 의원들의 통계 요약 계산
    
    Args:
        db: 데이터베이스 세션
        asset_group: 재산 구간 ('0-20 백분위', '20-40 백분위', '40-60 백분위', '60-80 백분위', '80-100 백분위')
        
    Returns:
        재산 구간별 통계 요약 딕셔너리
    """
    # 백분위 기반 자산 범위 계산
    percentile_ranges = get_asset_percentile_ranges(db)
    
    if not percentile_ranges or asset_group not in percentile_ranges:
        return {
            "avg_score": 0,
            "max_score": 0,
            "min_score": 0,
            "avg_asset": 0,
            "count": 0,
            "tier_distribution": {}
        }
    
    # 선택한 백분위 범위 가져오기
    asset_min, asset_max = percentile_ranges[asset_group]
    
    # 해당 재산 구간 의원들의 통계
    # get_legislators_by_asset_group와 같은 조건 적용
    if asset_group == "0-20 백분위":
        stats = db.query(
            func.avg(Legislator.overall_score).label("avg_score"),
            func.max(Legislator.overall_score).label("max_score"),
            func.min(Legislator.overall_score).label("min_score"),
            func.avg(Legislator.asset).label("avg_asset"),
            func.count(Legislator.id).label("count")
        ).filter(
            Legislator.asset >= asset_min,
            Legislator.asset <= asset_max
        ).first()
        
        # 티어 분포 계산
        tier_query = db.query(
            Legislator.tier,
            func.count(Legislator.id).label("count")
        ).filter(
            Legislator.asset >= asset_min,
            Legislator.asset <= asset_max
        ).group_by(
            Legislator.tier
        ).all()
    else:
        stats = db.query(
            func.avg(Legislator.overall_score).label("avg_score"),
            func.max(Legislator.overall_score).label("max_score"),
            func.min(Legislator.overall_score).label("min_score"),
            func.avg(Legislator.asset).label("avg_asset"),
            func.count(Legislator.id).label("count")
        ).filter(
            Legislator.asset > asset_min,
            Legislator.asset <= asset_max
        ).first()
        
        # 티어 분포 계산
        tier_query = db.query(
            Legislator.tier,
            func.count(Legislator.id).label("count")
        ).filter(
            Legislator.asset > asset_min,
            Legislator.asset <= asset_max
        ).group_by(
            Legislator.tier
        ).all()
    
    tier_distribution = {}
    for tier, count in tier_query:
        tier_distribution[tier] = count
    
    # 결과 딕셔너리 구성
    result = {
        "avg_score": round(stats.avg_score, 1) if stats.avg_score else 0,
        "max_score": round(stats.max_score, 1) if stats.max_score else 0,
        "min_score": round(stats.min_score, 1) if stats.min_score else 0,
        "avg_asset": round(stats.avg_asset / 100000000, 1) if stats.avg_asset else 0,  # 억 단위
        "count": stats.count or 0,
        "tier_distribution": tier_distribution
    }
    
    return result

def get_legislators_by_asset_group(db: Session, asset_group: str) -> List[Dict[str, Any]]:
    """
    특정 재산 구간 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        asset_group: 재산 구간 (0-20 백분위, 20-40 백분위, 40-60 백분위, 60-80 백분위, 80-100 백분위)
    
    Returns:
        의원 목록 (재산 내림차순 정렬)
    """
    # 재산 구간별 범위 조회
    percentile_ranges = get_asset_percentile_ranges(db)
    
    # 해당 구간이 유효한지 확인
    if asset_group not in percentile_ranges:
        return []
    
    # 재산 범위
    min_asset, max_asset = percentile_ranges[asset_group]
    
    # 해당 재산 구간에 속하는 의원 목록 조회 (재산 내림차순 정렬)
    legislators = db.query(Legislator).filter(
        Legislator.asset >= min_asset,
        Legislator.asset <= max_asset
    ).order_by(
        Legislator.asset.desc()
    ).all()
    
    # ORM 객체를 dict로 변환
    result = []
    for legislator in legislators:
        # 재산 값을 억 단위로 변환
        asset_in_billion = round(legislator.asset / 100000000, 2) if legislator.asset else 0
        
        # 이미지 URL을 썸네일용으로 최적화
        profile_image_url = legislator.profile_image_url
        if profile_image_url:
            # 파일명만 추출
            filename = profile_image_url.split('/')[-1]
            profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "thumb")
        else:
            profile_image_url = "/static/images/legislators/default.png"
            
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "party": legislator.poly_nm,
            "district": legislator.orig_nm,
            "term": legislator.reele_gbn_nm,
            "committee": legislator.cmit_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": profile_image_url,
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
            "asset": asset_in_billion
        })
    
    return result