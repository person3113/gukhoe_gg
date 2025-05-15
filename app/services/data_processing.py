from sqlalchemy.orm import Session
from typing import List, Dict, Any


def process_attendance_data(raw_data):
    # 출석 데이터 정리 및 가공
    # 출석률 계산
    # 반환: 처리된 출석 데이터
    pass

def process_speech_data(raw_data):
    # 발언 데이터 정리 및 가공
    # 발언 횟수, 키워드 분석
    # 반환: 처리된 발언 데이터
    pass

def process_bill_data(raw_data):
    """
    법안 데이터 정리 및 가공
    
    Args:
        raw_data: API로부터 받은 원본 법안 데이터
    
    Returns:
        처리된 법안 데이터 리스트
    """
    from app.db.database import SessionLocal
    from app.models.bill import Bill, BillCoProposer
    from app.models.legislator import Legislator
    
    db = SessionLocal()
    processed_bills = []
    
    try:
        # 각 법안 데이터 처리
        for bill_data in raw_data:
            try:
                # 대표발의자 처리 (쉼표로 구분된 여러 발의자 처리)
                main_proposers_str = bill_data.get("main_proposer", "")
                if not main_proposers_str:
                    print(f"대표발의자 정보가 없음: 법안: {bill_data.get('bill_name')}")
                    continue
                
                # 쉼표로 구분된 대표발의자 이름 파싱
                main_proposer_names = [name.strip() for name in main_proposers_str.split(',')]
                if not main_proposer_names:
                    print(f"대표발의자 정보 파싱 실패: {main_proposers_str}, 법안: {bill_data.get('bill_name')}")
                    continue
                
                # 첫 번째 대표발의자 찾기
                primary_proposer = None
                for name in main_proposer_names:
                    proposer = db.query(Legislator).filter(Legislator.hg_nm == name).first()
                    if proposer:
                        primary_proposer = proposer
                        break
                
                # 대표발의자를 하나도 찾지 못한 경우 스킵
                if not primary_proposer:
                    print(f"대표발의자를 찾을 수 없음: {main_proposers_str}, 법안: {bill_data.get('bill_name')}")
                    continue
                
                # MEMBER_LIST URL 추출
                member_list_url = bill_data.get("MEMBER_LIST", "")
                
                # 기존 법안 정보 확인
                existing_bill = db.query(Bill).filter(Bill.bill_no == bill_data.get("bill_no")).first()
                
                if existing_bill:
                    # 기존 법안 정보 업데이트
                    existing_bill.bill_name = bill_data.get("bill_name")
                    existing_bill.propose_dt = bill_data.get("propose_dt")
                    existing_bill.detail_link = bill_data.get("detail_link")
                    existing_bill.proposer = bill_data.get("proposer")
                    existing_bill.committee = bill_data.get("committee")
                    existing_bill.proc_result = bill_data.get("proc_result")
                    existing_bill.main_proposer_id = primary_proposer.id
                    existing_bill.member_list_url = member_list_url  # URL 업데이트
                    
                    bill = existing_bill
                else:
                    # 새 법안 정보 생성
                    bill = Bill(
                        bill_no=bill_data.get("bill_no"),
                        bill_name=bill_data.get("bill_name"),
                        propose_dt=bill_data.get("propose_dt"),
                        detail_link=bill_data.get("detail_link"),
                        proposer=bill_data.get("proposer"),
                        committee=bill_data.get("committee"),
                        proc_result=bill_data.get("proc_result"),
                        main_proposer_id=primary_proposer.id,
                        member_list_url=member_list_url  # URL 저장
                    )
                    db.add(bill)
                    db.flush()  # ID 할당을 위해 flush
                
                # 기존 공동발의자 삭제
                db.query(BillCoProposer).filter(BillCoProposer.bill_id == bill.id).delete()
                
                # 대표발의자 중 첫 번째를 제외한 나머지를 공동발의자로 등록
                for name in main_proposer_names:
                    if name == primary_proposer.hg_nm:
                        continue
                    
                    co_proposer = db.query(Legislator).filter(Legislator.hg_nm == name).first()
                    if co_proposer:
                        co_proposer_rel = BillCoProposer(
                            bill_id=bill.id,
                            legislator_id=co_proposer.id,
                            is_representative=True  # 대표발의자 여부 표시
                        )
                        db.add(co_proposer_rel)
                
                # 일반 공동발의자 처리
                co_proposers_str = bill_data.get("co_proposers", "")
                
                # 일반적인 경우: 콤마로 구분된 목록
                if co_proposers_str:
                    co_proposer_names = [name.strip() for name in co_proposers_str.split(',')]
                    
                    # 공동발의자 정보 DB에 저장
                    for name in co_proposer_names:
                        if not name or name in main_proposer_names:
                            continue
                        
                        # 공동발의자 정보 DB에서 조회
                        co_proposer = db.query(Legislator).filter(Legislator.hg_nm == name).first()
                        if co_proposer:
                            # 공동발의자 연결 정보 추가
                            co_proposer_rel = BillCoProposer(
                                bill_id=bill.id,
                                legislator_id=co_proposer.id,
                                is_representative=False  # 일반 공동발의자
                            )
                            db.add(co_proposer_rel)
                
                # 변경사항 저장
                db.commit()
                
                # 처리된 법안 정보 추가
                processed_bill = {
                    "id": bill.id,
                    "bill_no": bill.bill_no,
                    "bill_name": bill.bill_name,
                    "propose_dt": bill.propose_dt,
                    "detail_link": bill.detail_link,
                    "proposer": bill.proposer,
                    "committee": bill.committee,
                    "proc_result": bill.proc_result,
                    "main_proposer_id": bill.main_proposer_id,
                    "member_list_url": bill.member_list_url  # URL 정보 추가
                }
                processed_bills.append(processed_bill)
                
            except Exception as e:
                print(f"법안 처리 중 오류 발생: {str(e)}, 법안: {bill_data.get('bill_name')}")
                db.rollback()  # 오류 발생 시 롤백
                continue
        
        return processed_bills
    finally:
        db.close()

def process_vote_data(raw_data, age='22'):
    # 표결 데이터 정리 및 가공
    # 법안 ID를 기준으로 표결 정보 연결
    # 찬성/반대/기권 분석
    # 반환: 처리된 표결 데이터
    pass

def calculate_committee_processing_ratio(db: Session):
    # DB에서 위원회별 접수건수, 처리건수 데이터 조회
    # 처리 비율 계산 (처리건수/접수건수 * 100)
    # DB 업데이트
    pass