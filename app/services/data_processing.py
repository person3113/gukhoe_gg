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
    from app.services.bill_service import get_co_proposers_from_url  # 추가된 부분
    
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
                    existing_bill.bill_id = bill_data.get("bill_id", "")  # bill_id 필드 추가
                    existing_bill.bill_name = bill_data.get("bill_name")
                    existing_bill.propose_dt = bill_data.get("propose_dt")
                    existing_bill.detail_link = bill_data.get("detail_link")
                    existing_bill.proposer = bill_data.get("proposer")
                    existing_bill.committee = bill_data.get("committee")
                    existing_bill.proc_result = bill_data.get("proc_result")
                    existing_bill.main_proposer_id = primary_proposer.id
                    existing_bill.member_list_url = member_list_url
                    
                    bill = existing_bill
                else:
                    # 새 법안 정보 생성
                    bill = Bill(
                        bill_id=bill_data.get("bill_id", ""),  # bill_id 필드 추가
                        bill_no=bill_data.get("bill_no"),
                        bill_name=bill_data.get("bill_name"),
                        propose_dt=bill_data.get("propose_dt"),
                        detail_link=bill_data.get("detail_link"),
                        proposer=bill_data.get("proposer"),
                        committee=bill_data.get("committee"),
                        proc_result=bill_data.get("proc_result"),
                        main_proposer_id=primary_proposer.id,
                        member_list_url=member_list_url
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
                
                # 공동발의자 정보가 API에서 제공되는 경우
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
                # API에서 공동발의자 정보가 제공되지 않는 경우, member_list_url에서 가져오기
                elif member_list_url:
                    try:
                        print(f"공동발의자 정보가 비어있어 URL에서 파싱합니다: {member_list_url}")
                        url_co_proposer_names = get_co_proposers_from_url(member_list_url)
                        
                        for name in url_co_proposer_names:
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
                    except Exception as e:
                        print(f"공동발의자 URL 파싱 중 오류 발생: {str(e)}")
                
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
                    "member_list_url": bill.member_list_url
                }
                processed_bills.append(processed_bill)
                
            except Exception as e:
                print(f"법안 처리 중 오류 발생: {str(e)}, 법안: {bill_data.get('bill_name')}")
                db.rollback()  # 오류 발생 시 롤백
                continue
        
        return processed_bills
    finally:
        db.close()

def process_vote_data(raw_data, db=None):
    """
    표결 데이터 정리 및 가공
    
    Args:
        raw_data: API로부터 받은 원본 표결 데이터
        db: 데이터베이스 세션 (None인 경우 내부에서 생성)
    
    Returns:
        처리된 표결 데이터
    """
    from app.db.database import SessionLocal
    from app.models.vote import Vote, VoteResult
    from app.models.bill import Bill
    from app.models.legislator import Legislator
    
    if not raw_data:
        return None
    
    # DB 세션 생성 (외부에서 제공되지 않은 경우)
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        bill_id = raw_data.get("bill_id")
        vote_date = raw_data.get("vote_date")
        
        # 법안 ID로 법안 정보 조회
        bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if not bill:
            print(f"bill_id로 법안을 찾을 수 없음: {bill_id}, bill_no로 시도합니다.")
            # bill_no가 있는 경우 bill_no로도 시도
            if raw_data.get("bill_no"):
                bill = db.query(Bill).filter(Bill.bill_no == raw_data.get("bill_no")).first()
        
        # 기존 표결 정보 확인
        existing_vote = db.query(Vote).filter(
            Vote.bill_id == bill.id,
            Vote.vote_date == vote_date
        ).first()
        
        if existing_vote:
            # 기존 표결 결과 삭제
            db.query(VoteResult).filter(
                VoteResult.vote_id == existing_vote.id
            ).delete()
            
            vote = existing_vote
        else:
            # 새 표결 정보 생성
            vote = Vote(
                vote_date=vote_date,
                bill_id=bill.id
            )
            db.add(vote)
            db.flush()  # ID 할당을 위해 flush
        
        # 표결 결과 처리
        results = raw_data.get("results", [])
        processed_count = 0
        missing_legislators = []
        
        for result in results:
            # 의원 이름으로 의원 정보 조회
            legislator_name = result.get("legislator_name", "")
            legislator = db.query(Legislator).filter(
                Legislator.hg_nm == legislator_name
            ).first()
            
            if not legislator:
                missing_legislators.append(legislator_name)
                continue
            
            # 표결 결과 저장
            vote_result = VoteResult(
                vote_id=vote.id,
                legislator_id=legislator.id,
                result_vote_mod=result.get("result", "")
            )
            db.add(vote_result)
            processed_count += 1
        
        # 변경사항 저장
        db.commit()
        
        # 처리 통계 출력
        print(f"법안 {bill_id}의 표결 결과 처리 완료")
        print(f"- 전체 표결 수: {len(results)}")
        print(f"- 처리된 표결 수: {processed_count}")
        if missing_legislators:
            print(f"- DB에 없는 의원 수: {len(missing_legislators)}")
            print(f"- 미확인 의원: {', '.join(missing_legislators[:5])}{'...' if len(missing_legislators) > 5 else ''}")
        
        # 처리 결과 반환
        processed_data = {
            "vote_id": vote.id,
            "bill_id": bill.id,
            "vote_date": vote_date,
            "total_results": len(results),
            "processed_results": processed_count,
            "missing_legislators": len(missing_legislators)
        }
        
        return processed_data
        
    except Exception as e:
        print(f"표결 데이터 처리 중 오류 발생: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 내부에서 생성한 DB 세션인 경우에만 닫기
        if close_db:
            db.close()

def calculate_committee_processing_ratio(db: Session):
    # DB에서 위원회별 접수건수, 처리건수 데이터 조회
    # 처리 비율 계산 (처리건수/접수건수 * 100)
    # DB 업데이트
    pass