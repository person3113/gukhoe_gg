from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import join

from app.models.vote import VoteResult, Vote
from app.models.bill import Bill

def get_vote_results(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    """
    특정 의원의 본회의 표결 결과 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        표결 결과 목록
    """
    # 표결 결과, 표결, 법안 정보 조인하여 조회
    query = db.query(
        VoteResult, 
        Vote.vote_date, 
        Bill.bill_name, 
        Bill.committee,
        Bill.detail_link,
        Bill.law_title  # law_title 추가
    ).join(
        Vote, VoteResult.vote_id == Vote.id
    ).join(
        Bill, Vote.bill_id == Bill.id
    ).filter(
        VoteResult.legislator_id == legislator_id
    ).order_by(
        Vote.vote_date.desc()
    )
    
    # 결과 데이터 구성
    result = []
    for vote_result, vote_date, bill_name, committee, detail_link, law_title in query:
        result.append({
            "vote_date": vote_date,
            "bill_name": bill_name,
            "law_title": law_title or bill_name,  # law_title이 없는 경우 bill_name 사용
            "committee": committee,
            "result": vote_result.result_vote_mod,
            "detail_link": detail_link
        })
    
    return result