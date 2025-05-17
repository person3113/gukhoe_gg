from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.bill import Bill, BillCoProposer

def get_representative_bills(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원이 대표 발의한 법안 목록 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        대표 발의안 목록과 총 발의 개수를 포함한 딕셔너리
    """
    # 첫 번째 대표발의자로 등록된 법안 조회
    primary_bills = db.query(Bill).filter(
        Bill.main_proposer_id == legislator_id
    ).all()
    
    # 공동 대표발의자로 등록된 법안 ID 조회
    co_representative_bill_ids = db.query(BillCoProposer.bill_id).filter(
        BillCoProposer.legislator_id == legislator_id,
        BillCoProposer.is_representative == True
    ).all()
    co_representative_bill_ids = [id[0] for id in co_representative_bill_ids]
    
    # 공동 대표발의자로 등록된 법안 조회
    co_representative_bills = []
    if co_representative_bill_ids:
        co_representative_bills = db.query(Bill).filter(
            Bill.id.in_(co_representative_bill_ids)
        ).all()
    
    # 모든 대표발의 법안 합치기
    all_bills = primary_bills + co_representative_bills
    
    # 결과 리스트 구성
    bill_list = []
    for bill in all_bills:
        bill_list.append({
            "id": bill.id,
            "bill_no": bill.bill_no,
            "bill_name": bill.bill_name,
            "law_title": bill.law_title or bill.bill_name,  # law_title이 없는 경우 bill_name 사용
            "propose_dt": bill.propose_dt,
            "committee": bill.committee,
            "status": format_bill_status(bill),
            "detail_link": bill.detail_link
        })
    
    # 제안일 기준 내림차순 정렬
    bill_list.sort(key=lambda x: x["propose_dt"] if x["propose_dt"] else "", reverse=True)
    
    # 결과에 법안 목록과 총 개수를 포함하여 반환
    result = {
        "bills": bill_list,
        "total_count": len(bill_list)
    }
    
    return result

def get_co_sponsored_bills(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원이 공동 발의한 법안 목록 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 국회의원 ID
    
    Returns:
        공동 발의안 목록과 총 발의 개수를 포함한 딕셔너리
    """
    # 공동발의한 법안 ID 목록 조회
    bill_ids = db.query(BillCoProposer.bill_id).filter(
        BillCoProposer.legislator_id == legislator_id
    ).all()
    
    # ID 리스트로 변환
    bill_ids = [bid[0] for bid in bill_ids]
    
    # 법안 정보 조회
    bills = db.query(Bill).filter(
        Bill.id.in_(bill_ids)
    ).order_by(
        Bill.propose_dt.desc()  # 최신 발의안이 상단에 위치하도록 정렬
    ).all()
    
    # 결과 데이터 구성
    bill_list = []
    for bill in bills:
        # 공동발의자 수 계산 (데이터베이스에 저장된 공동발의자)
        co_proposer_count = db.query(BillCoProposer).filter(
            BillCoProposer.bill_id == bill.id
        ).count()
        
        # member_list_url이 있는지 확인
        has_additional_proposers = bool(bill.member_list_url)
        
        bill_list.append({
            "bill_id": bill.id,
            "bill_no": bill.bill_no,
            "bill_name": bill.bill_name,
            "law_title": bill.law_title or bill.bill_name,  # law_title이 없으면 bill_name 사용
            "propose_dt": bill.propose_dt,
            "detail_link": bill.detail_link,
            "proposer": bill.proposer,
            "committee": bill.committee,
            "status": format_bill_status(bill),
            "co_proposer_count": co_proposer_count,
            "has_additional_proposers": has_additional_proposers,
            "member_list_url": bill.member_list_url  # 추가 공동발의자 목록 URL
        })
    
    # 결과에 법안 목록과 총 개수를 포함하여 반환
    result = {
        "bills": bill_list,
        "total_count": len(bill_list)
    }
    
    return result

def get_co_proposers_from_url(url: str) -> List[str]:
    """
    공동발의자 목록 페이지에서 발의자 이름 추출
    
    Args:
        url: 공동발의자 목록 페이지 URL
        
    Returns:
        공동발의자 이름 목록
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 페이지 요청
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 찬성의원 섹션 찾기 (div class="links textType02 mt30" 내 p 태그에 '찬성의원 명단'이라는 텍스트가 있음)
        approval_section = None
        for div in soup.find_all('div', class_='links textType02 mt30'):
            p_tag = div.find('p')
            if p_tag and '찬성의원 명단' in p_tag.text:
                approval_section = div
                break
        
        proposer_names = []
        if approval_section:
            # 모든 a 태그에서 이름 추출
            for a_tag in approval_section.find_all('a'):
                # 태그 텍스트에서 이름 추출 (예: "김영진(더불어민주당/金榮鎭)" 에서 "김영진" 추출)
                full_text = a_tag.text.strip()
                name = full_text.split('(')[0].strip()
                proposer_names.append(name)
        
        return proposer_names
        
    except Exception as e:
        print(f"공동발의자 목록 파싱 오류: {str(e)}")
        return []

def format_bill_status(bill: Any) -> str:
    """
    법안 상태(계류중, 가결, 폐기 등) 표시 포맷 변환
    
    Args:
        bill: 법안 객체 또는 딕셔너리
    
    Returns:
        포맷팅된 법안 상태 문자열
    """
    # 객체인 경우와 딕셔너리인 경우 모두 처리
    proc_result = bill.proc_result if hasattr(bill, 'proc_result') else bill.get('proc_result')
    
    if not proc_result:
        return "계류중"
    
    # 일반적인 상태 타입
    status_map = {
        "원안가결": "원안가결",
        "수정가결": "수정가결",
        "대안반영폐기": "대안반영",
        "폐기": "폐기",
        "부결": "부결",
        "임기만료폐기": "임기만료"
    }
    
    # 매핑된 상태값 반환 (없으면 원래 값 그대로 반환)
    return status_map.get(proc_result, proc_result)