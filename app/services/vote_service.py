from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.vote import VoteResult

def get_vote_results(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(VoteResult)로 특정 의원의 본회의 표결 결과 조회
    # 반환: 표결 결과 목록
    pass