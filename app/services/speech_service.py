from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.speech import SpeechKeyword, SpeechByMeeting

def get_top_keywords(db: Session, legislator_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    특정 의원의 상위 발언 키워드 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
        limit: 조회할 상위 키워드 수
    
    Returns:
        키워드 및 발언 횟수 목록
    """
    # 키워드 조회 (count 기준 내림차순 정렬)
    keywords = db.query(SpeechKeyword).filter(
        SpeechKeyword.legislator_id == legislator_id
    ).order_by(
        SpeechKeyword.count.desc()
    ).limit(limit).all()
    
    # 결과 데이터 구성
    result = []
    for keyword in keywords:
        result.append({
            "keyword": keyword.keyword,
            "count": keyword.count
        })
    
    return result

def get_speech_by_meeting_type(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    """
    특정 의원의 회의 구분별 발언 수 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        회의 구분별 발언 수 목록
    """
    # 회의 구분별 발언 조회
    speeches = db.query(SpeechByMeeting).filter(
        SpeechByMeeting.legislator_id == legislator_id
    ).all()
    
    # 결과 데이터 구성 - Total과 빈 문자열 제외
    result = []
    for speech in speeches:
        # Total이나 빈 문자열 제외
        if speech.meeting_type != "Total" and speech.meeting_type != "":
            result.append({
                "meeting_type": speech.meeting_type,
                "count": speech.count
            })
    
    return result