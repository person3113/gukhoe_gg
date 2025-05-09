from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.bill import Bill, BillCoProposer

def get_representative_bills(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    """
    특정 의원이 대표 발의한 법안 목록 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        대표 발의안 목록
    """
    # 의원이 대표 발의한 법안 목록 조회
    bills = db.query(Bill).filter(
        Bill.main_proposer_id == legislator_id
    ).order_by(
        Bill.propose_dt.desc()  # 제안일 기준 내림차순 정렬
    ).all()
    
    # 결과 리스트 구성
    result = []
    for bill in bills:
        result.append({
            "id": bill.id,
            "bill_no": bill.bill_no,
            "bill_name": bill.bill_name,
            "law_title": bill.law_title or bill.bill_name,  # law_title이 없는 경우 bill_name 사용
            "propose_dt": bill.propose_dt,
            "committee": bill.committee,
            "status": format_bill_status(bill),
            "detail_link": bill.detail_link
        })
    
    return result

def get_co_sponsored_bills(db: Session, legislator_id: int) -> List[Dict[str, Any]]:
    # 호출: db.query(BillCoProposer)로 특정 의원이 공동 발의한 법안 목록 조회
    # 반환: 공동 발의안 목록
    pass

def format_bill_status(bill: Bill) -> str:
    """
    법안 상태(계류중, 가결, 폐기 등) 표시 포맷 변환
    
    Args:
        bill: 법안 객체
    
    Returns:
        포맷팅된 법안 상태 문자열
    """
    status = bill.proc_result
    
    # 상태값이 없는 경우 기본값 설정
    if not status:
        return "계류중"
    
    # 상태값 매핑
    if "가결" in status:
        return "가결"
    elif "폐기" in status:
        return "폐기"
    elif "철회" in status:
        return "철회"
    elif "반영" in status:
        return "대안반영"
    else:
        return status