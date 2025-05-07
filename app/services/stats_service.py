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
    # 호출: db.query(Legislator)로 정당별 의원 그룹화
    # 정당별 특정 통계 평균 계산
    # 반환: 정당별 평균 통계 딕셔너리
    pass

def get_term_average_stats(db: Session, stat: str = 'overall_score') -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 초선/재선별 의원 그룹화
    # 초선/재선별 특정 통계 평균 계산
    # 반환: 초선/재선별 평균 통계 딕셔너리
    pass

### 잡다한 랭킹 - 정당 ###
def get_party_average_scores(db: Session) -> Dict[str, float]:
    """
    정당별 평균 종합점수 조회
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        정당별 평균 종합점수 딕셔너리
    """
    # 정당 목록 조회
    parties = db.query(Legislator.poly_nm).distinct().all()
    party_list = [party[0] for party in parties]
    
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
    정당별 평균 대표발의안수 조회
    
    Args:
        db: 데이터베이스 세션
    
    Returns:
        정당별 평균 대표발의안수 딕셔너리
    """
    # 정당 목록 조회
    parties = db.query(Legislator.poly_nm).distinct().all()
    party_list = [party[0] for party in parties]
    
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
    # 호출: db.query(Committee)로 위원회별 법안 접수/처리 비율 계산
    # 반환: 위원회별 처리 비율 딕셔너리
    pass

def get_committee_average_scores(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Committee, CommitteeMember, Legislator)로 위원회별 평균 종합점수 계산
    # 반환: 위원회별 평균 종합점수 딕셔너리
    pass

def get_committee_stats_summary(db: Session, committee_name: str) -> Dict[str, Any]:
    # 호출: db.query(Committee, CommitteeMember, Legislator)로 특정 위원회 통계 요약 조회
    # 반환: 위원회 통계 요약 딕셔너리
    pass

def get_legislators_by_committee(db: Session, committee_name: str) -> List[Dict[str, Any]]:
    # 호출: db.query(CommitteeMember, Legislator)로 특정 위원회 소속 의원 목록 조회
    # 반환: 의원 목록
    pass

### 잡다한 랭킹 - 초선/재선 ###
def get_tier_distribution_by_term(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 초선/재선별 티어 분포 계산
    # 반환: 초선/재선별 티어 분포 딕셔너리
    pass

def get_term_average_assets(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 초선/재선별 평균 재산 계산
    # 반환: 초선/재선별 평균 재산 딕셔너리
    pass

def get_term_stats_summary(db: Session, term: str) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 선수 의원들의 통계 요약 계산
    # 반환: 선수별 통계 요약 딕셔너리
    pass

def get_legislators_by_term(db: Session, term: str) -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 특정 선수 의원 목록 조회
    # 반환: 의원 목록
    pass

### 잡다한 랭킹 - 성별 ###
def get_tier_distribution_by_gender(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 성별 티어 분포 계산
    # 반환: 성별 티어 분포 딕셔너리
    pass

def get_gender_average_assets(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 성별 평균 재산 계산
    # 반환: 성별 평균 재산 딕셔너리
    pass

def get_gender_stats_summary(db: Session, gender: str) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 성별 의원들의 통계 요약 계산
    # 반환: 성별 통계 요약 딕셔너리
    pass

def get_legislators_by_gender(db: Session, gender: str) -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 특정 성별 의원 목록 조회
    # 반환: 의원 목록
    pass

### 잡다한 랭킹 - 나이별 ###
def get_age_average_scores(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 나이대별 평균 종합점수 계산
    # 반환: 나이대별 평균 종합점수 딕셔너리
    pass

def get_age_average_assets(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 나이대별 평균 재산 계산
    # 반환: 나이대별 평균 재산 딕셔너리
    pass

def get_age_stats_summary(db: Session, age_group: str) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 나이대 의원들의 통계 요약 계산
    # 반환: 나이대별 통계 요약 딕셔너리
    pass

def get_legislators_by_age_group(db: Session, age_group: str) -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 특정 나이대 의원 목록 조회
    # 반환: 의원 목록
    pass

### 잡다한 랭킹 - 재산 ###
def get_score_asset_correlation(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 활동점수와 재산의 상관관계 데이터 계산
    # 반환: 상관관계 데이터 딕셔너리
    pass

def get_party_asset_ratio(db: Session) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 정당별 재산 비율 계산
    # 반환: 정당별 재산 비율 딕셔너리
    pass

def get_asset_stats_summary(db: Session, asset_group: str) -> Dict[str, Any]:
    # 호출: db.query(Legislator)로 특정 재산 구간 의원들의 통계 요약 계산
    # 반환: 재산 구간별 통계 요약 딕셔너리
    pass

def get_legislators_by_asset_group(db: Session, asset_group: str) -> List[Dict[str, Any]]:
    # 호출: db.query(Legislator)로 특정 재산 구간 의원 목록 조회
    # 반환: 의원 목록
    pass