from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.bill import Bill, BillCoProposer

def get_representative_bills(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(Bill)로 특정 의원이 대표 발의한 법안 목록 조회
    # 반환: 대표 발의안 목록
    pass

def get_co_sponsored_bills(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(BillCoProposer)로 특정 의원이 공동 발의한 법안 목록 조회
    # 반환: 공동 발의안 목록
    pass

def format_bill_status(bill: Dict[str, Any]) -> str:
    # 법안 상태(계류중, 가결, 폐기 등) 표시 포맷 변환
    # 반환: 포맷팅된 법안 상태 문자열
    pass