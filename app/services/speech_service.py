from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.speech import SpeechKeyword, SpeechByMeeting

def get_top_keywords(db: Session, legislator_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    # 호출: db.query(SpeechKeyword)로 특정 의원의 상위 발언 키워드 조회
    # 반환: 키워드 및 발언 횟수 목록
    pass

def get_speech_by_meeting_type(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(SpeechByMeeting)로 특정 의원의 회의 구분별 발언 수 조회
    # 반환: 회의 구분별 발언 수 목록
    pass