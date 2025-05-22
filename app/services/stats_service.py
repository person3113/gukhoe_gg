from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Dict, Any, Optional

from app.models.bill import Bill
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeMember

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
                Legislator.poly_nm == party
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
                Legislator.reele_gbn_nm == term
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
        의원 목록
    """
    # 해당 정당 소속 의원 조회
    legislators = db.query(Legislator).filter(
        Legislator.poly_nm == party_name
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
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
        의원 목록
    """
    # 위원회 정보 조회
    committee = db.query(Committee).filter(Committee.dept_nm == committee_name).first()
    
    if not committee:
        return []
    
    # 위원회 소속 의원 ID 조회
    member_ids = db.query(CommitteeMember.legislator_id).filter(
        CommitteeMember.committee_id == committee.id
    ).all()
    member_ids = [mid[0] for mid in member_ids]
    
    if not member_ids:
        return []
    
    # 의원 정보 조회
    legislators = db.query(Legislator).filter(
        Legislator.id.in_(member_ids)
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
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
            Legislator.reele_gbn_nm == term
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
        term: 선수 구분 (초선, 재선 등)
        
    Returns:
        의원 목록
    """
    # 해당 선수 의원 목록 조회
    legislators = db.query(Legislator).filter(
        Legislator.reele_gbn_nm == term
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
            "asset": round(legislator.asset / 100000000, 1) if legislator.asset else 0  # 억 단위
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
            Legislator.sex_gbn_nm == gender
        ).scalar()
        
        result[gender] = round(avg_asset / 100000000, 1) if avg_asset else 0
    
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
        의원 목록
    """
    # 해당 성별 의원 목록 조회
    legislators = db.query(Legislator).filter(
        Legislator.sex_gbn_nm == gender
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
            "asset": round(legislator.asset / 100000000, 1) if legislator.asset else 0  # 억 단위
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
            Legislator.bth_date.between(str(min_year), str(max_year))
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
    특정 나이대 의원 목록 조회
    
    Args:
        db: 데이터베이스 세션
        age_group: 나이대 ('30대 이하', '40대', '50대', '60대', '70대 이상')
        
    Returns:
        의원 목록
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
        return []
    
    # 해당 나이대 의원 목록 조회
    legislators = db.query(Legislator).filter(
        Legislator.bth_date.between(str(birth_year_min), str(birth_year_max))
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
            "asset": round(legislator.asset / 100000000, 1) if legislator.asset else 0  # 억 단위
        })
    
    return result

def get_score_asset_correlation(db: Session) -> Dict[str, Any]:
    """
    활동점수와 재산의 상관관계 데이터 계산
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        상관관계 데이터 딕셔너리
    """
    # 의원별 점수와 재산 데이터 조회
    legislators = db.query(
        Legislator.id,
        Legislator.hg_nm,
        Legislator.overall_score,
        Legislator.asset
    ).all()
    
    # 데이터 포인트 구성
    data_points = []
    for legislator in legislators:
        if legislator.overall_score is not None and legislator.asset is not None:
            data_points.append({
                "id": legislator.id,
                "name": legislator.hg_nm,
                "score": round(legislator.overall_score, 1),
                "asset": round(legislator.asset / 100000000, 1)  # 억 단위
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
    # 전체 재산 합계 조회
    total_asset = db.query(func.sum(Legislator.asset)).scalar() or 1  # 0으로 나누기 방지
    
    # 정당별 재산 합계 조회
    party_assets = db.query(
        Legislator.poly_nm,
        func.sum(Legislator.asset).label("total_asset"),
        func.count(Legislator.id).label("count")
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

def get_asset_stats_summary(db: Session, asset_group: str) -> Dict[str, Any]:
    """
    특정 재산 구간 의원들의 통계 요약 계산
    
    Args:
        db: 데이터베이스 세션
        asset_group: 재산 구간 ('1억 미만', '1억~10억', '10억~50억', '50억~100억', '100억 이상')
        
    Returns:
        재산 구간별 통계 요약 딕셔너리
    """
    # 재산 구간에 따른 범위 설정 (단위: 원)
    if asset_group == "1억 미만":
        asset_min, asset_max = 0, 100000000
    elif asset_group == "1억~10억":
        asset_min, asset_max = 100000000, 1000000000
    elif asset_group == "10억~50억":
        asset_min, asset_max = 1000000000, 5000000000
    elif asset_group == "50억~100억":
        asset_min, asset_max = 5000000000, 10000000000
    elif asset_group == "100억 이상":
        asset_min, asset_max = 10000000000, 9999999999999
    else:
        return {
            "avg_score": 0,
            "max_score": 0,
            "min_score": 0,
            "avg_asset": 0,
            "count": 0,
            "tier_distribution": {}
        }
    
    # 해당 재산 구간 의원들의 통계
    stats = db.query(
        func.avg(Legislator.overall_score).label("avg_score"),
        func.max(Legislator.overall_score).label("max_score"),
        func.min(Legislator.overall_score).label("min_score"),
        func.avg(Legislator.asset).label("avg_asset"),
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.asset.between(asset_min, asset_max)
    ).first()
    
    # 티어 분포 계산
    tier_query = db.query(
        Legislator.tier,
        func.count(Legislator.id).label("count")
    ).filter(
        Legislator.asset.between(asset_min, asset_max)
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
        asset_group: 재산 구간 ('1억 미만', '1억~10억', '10억~50억', '50억~100억', '100억 이상')
        
    Returns:
        의원 목록
    """
    # 재산 구간에 따른 범위 설정 (단위: 원)
    if asset_group == "1억 미만":
        asset_min, asset_max = 0, 100000000
    elif asset_group == "1억~10억":
        asset_min, asset_max = 100000000, 1000000000
    elif asset_group == "10억~50억":
        asset_min, asset_max = 1000000000, 5000000000
    elif asset_group == "50억~100억":
        asset_min, asset_max = 5000000000, 10000000000
    elif asset_group == "100억 이상":
        asset_min, asset_max = 10000000000, 9999999999999
    else:
        return []
    
    # 해당 재산 구간 의원 목록 조회
    legislators = db.query(Legislator).filter(
        Legislator.asset.between(asset_min, asset_max)
    ).order_by(
        Legislator.overall_score.desc()
    ).all()
    
    # 결과 리스트 구성
    result = []
    for legislator in legislators:
        result.append({
            "id": legislator.id,
            "name": legislator.hg_nm,
            "tier": legislator.tier,
            "overall_rank": legislator.overall_rank,
            "party": legislator.poly_nm,
            "profile_image_url": legislator.profile_image_url or "/static/images/legislators/default.png",
            "overall_score": round(legislator.overall_score, 1) if legislator.overall_score else 0,
            "participation_score": round(legislator.participation_score, 1) if legislator.participation_score else 0,
            "legislation_score": round(legislator.legislation_score, 1) if legislator.legislation_score else 0,
            "speech_score": round(legislator.speech_score, 1) if legislator.speech_score else 0,
            "voting_score": round(legislator.voting_score, 1) if legislator.voting_score else 0,
            "cooperation_score": round(legislator.cooperation_score, 1) if legislator.cooperation_score else 0,
            "asset": round(legislator.asset / 100000000, 1) if legislator.asset else 0  # 억 단위
        })
    
    return result