from sqlalchemy.orm import Session
from typing import List, Dict, Any
from scripts.calculate_scores import calculate_participation_scores

def process_attendance_data(raw_data: List[Dict[str, Any]], db: Session) -> None:
    """
    출석 데이터 처리 및 DB 저장
    
    Args:
        raw_data: 출석 데이터 리스트
        db: 데이터베이스 세션
    """
    from app.models.attendance import Attendance
    from app.models.legislator import Legislator
    
    try:
        processed_count = 0
        skipped_count = 0
        
        # 상임위와 본회의 데이터를 분리
        plenary_data = [data for data in raw_data if data['meeting_type'] == '본회의']
        standing_data = [data for data in raw_data if data['meeting_type'] == '상임위']
        
        # 의원 이름 캐시
        legislator_name_map = {}
        
        print(f"처리할 본회의 데이터: {len(plenary_data)}개")
        print(f"처리할 상임위 데이터: {len(standing_data)}개")
        
        # 본회의 데이터 처리 (그대로 추가)
        for data in plenary_data:
            legislator_name = data['legislator_name']
            
            # 의원 정보 조회 (캐시에 없으면 DB 조회)
            if legislator_name not in legislator_name_map:
                legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
                if not legislator:
                    print(f"경고: {legislator_name} 의원을 DB에서 찾을 수 없습니다.")
                    skipped_count += 1
                    continue
                legislator_name_map[legislator_name] = legislator
            else:
                legislator = legislator_name_map[legislator_name]
            
            # 새 데이터 추가
            new_attendance = Attendance(
                legislator_id=legislator.id,
                committee_id=None,
                meeting_type='본회의',
                status=data['status'],
                count=data.get('count', 0),
                meeting_date=None
            )
            db.add(new_attendance)
            processed_count += 1
        
        # 상임위 데이터 처리 (같은 의원-상태 조합이면 합산)
        # 의원별, 상태별로 데이터 정리
        standing_summary = {}
        for data in standing_data:
            legislator_name = data['legislator_name']
            status = data['status']
            
            # 의원 정보 조회 (캐시에 없으면 DB 조회)
            if legislator_name not in legislator_name_map:
                legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
                if not legislator:
                    print(f"경고: {legislator_name} 의원을 DB에서 찾을 수 없습니다.")
                    skipped_count += 1
                    continue
                legislator_name_map[legislator_name] = legislator
            else:
                legislator = legislator_name_map[legislator_name]
            
            # 의원별, 상태별 카운트 합산
            key = (legislator.id, status)
            if key not in standing_summary:
                standing_summary[key] = 0
            standing_summary[key] += data.get('count', 0)
        
        # 합산된 상임위 데이터 저장
        for (legislator_id, status), count in standing_summary.items():
            legislator_name = next((name for name, leg in legislator_name_map.items() if leg.id == legislator_id), "Unknown")
            print(f"상임위 합산 데이터 추가: {legislator_name}, {status}: {count}회")
            
            new_attendance = Attendance(
                legislator_id=legislator_id,
                committee_id=None,
                meeting_type='상임위',
                status=status,
                count=count,
                meeting_date=None
            )
            db.add(new_attendance)
            processed_count += 1
        
        # 변경사항 커밋
        db.commit()
        print(f"\n=== 출석 데이터 처리 결과 ===")
        print(f"추가: {processed_count}개")
        print(f"건너뜀: {skipped_count}개")
        
        # 출석 데이터가 추가되었으면 참여 점수 재계산
        if processed_count > 0:
            print("참여 점수 재계산 중...")
            from scripts.calculate_scores import calculate_participation_scores
            calculate_participation_scores(db)
            print("참여 점수 재계산 완료")
        
    except Exception as e:
        db.rollback()
        print(f"출석 데이터 처리 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def process_speech_data(raw_data, db: Session):
    # 발언 데이터 정리 및 가공
    # 발언 횟수, 키워드 분석
    # 반환: 처리된 발언 데이터
    """
    발언 데이터 정리 및 가공하여 DB에 저장
    
    Args:
        raw_data: 회의별 발언 데이터 리스트
        db: 데이터베이스 세션
    """
    from app.models.speech import SpeechByMeeting
    from app.models.legislator import Legislator
    
    try:
        # 결과 저장용 딕셔너리: {의원ID: Total 값}
        total_speeches = {}
        processed_count = 0
        skipped_count = 0
        duplicated_count = 0
        
        # 의원 이름 목록 - 각 의원 정보를 한 번만 조회하기 위함
        legislator_name_map = {}
        
        # 각 발언 데이터를 처리
        for data in raw_data:
            legislator_name = data['legislator_name']
            
            # 의원 정보가 캐시에 없으면 DB에서 조회
            if legislator_name not in legislator_name_map:
                legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
                if not legislator:
                    print(f"경고: {legislator_name} 의원을 DB에서 찾을 수 없습니다.")
                    skipped_count += 1
                    continue
                legislator_name_map[legislator_name] = legislator
            else:
                legislator = legislator_name_map[legislator_name]
            
            if not legislator:
                skipped_count += 1
                continue
                
            # 'Total'은 따로 저장해두고, speech_score 계산에 사용
            if data['meeting_type'] == 'Total':
                total_speeches[legislator.id] = data['count']
                
            # DB에 저장 (Total 포함)
            existing_speech = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id,
                SpeechByMeeting.meeting_type == data['meeting_type']
            ).first()
            
            if existing_speech:
                # 기존 데이터가 있으면 값을 더해주거나 최대값을 선택
                print(f"중복 데이터 발견: {legislator.hg_nm} - {data['meeting_type']} (기존: {existing_speech.count}, 새로운: {data['count']})")
                
                # 더 큰 값을 선택하거나, 합산하거나, 최신 값으로 업데이트
                # 여기서는 더 큰 값을 선택하는 방식으로 처리
                if data['count'] > existing_speech.count:
                    existing_speech.count = data['count']
                    print(f"  -> 더 큰 값으로 업데이트: {data['count']}")
                else:
                    print(f"  -> 기존 값 유지: {existing_speech.count}")
                    
                duplicated_count += 1
            else:
                # 새 데이터 추가
                new_speech = SpeechByMeeting(
                    legislator_id=legislator.id,
                    meeting_type=data['meeting_type'],
                    count=data['count']
                )
                db.add(new_speech)
                print(f"새 데이터 추가: {legislator.hg_nm} - {data['meeting_type']}: {data['count']}")
                
            processed_count += 1
        
        # 변경사항 커밋
        db.commit()
        print(f"\n=== 처리 결과 ===")
        print(f"처리 완료: {processed_count}개")
        print(f"건너뜀: {skipped_count}개")
        print(f"중복 업데이트: {duplicated_count}개")
        print(f"의원별 Total 발언 수: {len(total_speeches)}명")
        
    except Exception as e:
        db.rollback()
        print(f"발언 데이터 처리 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def process_keyword_data(raw_data: List[Dict[str, Any]], db: Session):
    """
    발언 키워드 데이터 정리 및 가공하여 DB에 저장
    
    Args:
        raw_data: 키워드 데이터 리스트
        db: 데이터베이스 세션
    """
    from app.models.speech import SpeechKeyword
    from app.models.legislator import Legislator
    
    try:
        processed_count = 0
        skipped_count = 0
        updated_count = 0
        
        # 의원 이름 캐시
        legislator_name_map = {}
        
        # 각 키워드 데이터를 처리
        for data in raw_data:
            legislator_name = data['legislator_name']
            
            # 의원 정보가 캐시에 없으면 DB에서 조회
            if legislator_name not in legislator_name_map:
                legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
                if not legislator:
                    print(f"경고: {legislator_name} 의원을 DB에서 찾을 수 없습니다.")
                    skipped_count += 1
                    continue
                legislator_name_map[legislator_name] = legislator
            else:
                legislator = legislator_name_map[legislator_name]
            
            if not legislator:
                skipped_count += 1
                continue
            
            # 기존 키워드 데이터 확인
            existing_keyword = db.query(SpeechKeyword).filter(
                SpeechKeyword.legislator_id == legislator.id,
                SpeechKeyword.keyword == data['keyword']
            ).first()
            
            if existing_keyword:
                # 기존 데이터가 있으면 값을 비교하여 업데이트
                if existing_keyword.count != data['count']:
                    print(f"키워드 업데이트: {legislator.hg_nm} - '{data['keyword']}' (기존: {existing_keyword.count}, 새로운: {data['count']})")
                    existing_keyword.count = data['count']
                    updated_count += 1
                else:
                    print(f"동일한 데이터 스킵: {legislator.hg_nm} - '{data['keyword']}': {data['count']}")
            else:
                # 새 키워드 데이터 추가
                new_keyword = SpeechKeyword(
                    legislator_id=legislator.id,
                    keyword=data['keyword'],
                    count=data['count']
                )
                db.add(new_keyword)
                print(f"새 키워드 추가: {legislator.hg_nm} - '{data['keyword']}': {data['count']}")
                processed_count += 1
        
        # 변경사항 커밋
        db.commit()
        print(f"\n=== 키워드 처리 결과 ===")
        print(f"새로 추가: {processed_count}개")
        print(f"업데이트: {updated_count}개")
        print(f"건너뜀: {skipped_count}개")
        
    except Exception as e:
        db.rollback()
        print(f"키워드 데이터 처리 오류: {str(e)}")
        import traceback
        traceback.print_exc()

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