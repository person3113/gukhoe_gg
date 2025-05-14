from sqlalchemy.orm import Session

def process_attendance_data(raw_data):
    # 출석 데이터 정리 및 가공
    # 출석률 계산
    # 반환: 처리된 출석 데이터
    pass

def process_speech_data(raw_data, type=None):
    # 발언 데이터 정리 및 가공
    # 발언 횟수, 키워드 분석
    # 반환: 처리된 발언 데이터
    """
    발언 데이터 정리 및 가공
    
    Args:
        raw_data: 원시 데이터
        type: 데이터 유형 ("keywords" 또는 "by_meeting")
    
    Returns:
        처리된 발언 데이터
    """
    """
    발언 데이터 정리 및 가공
    
    Args:
        raw_data: 파싱된 회의별 발언 데이터
        db: 데이터베이스 세션 (None인 경우 새 세션 생성)
    
    Returns:
        처리된 발언 데이터
    """
    from app.db.database import SessionLocal
    from app.models.speech import SpeechByMeeting
    from app.models.legislator import Legislator
    
    # DB 세션 생성 (인자로 받지 않은 경우)
    if db is None:
        db = SessionLocal()
        should_close_db = True
    else:
        should_close_db = False
    
    try:
        print(f"발언 데이터 처리 시작: {len(raw_data)}개 항목")
        
        # 의원 이름별 ID 매핑 생성
        legislator_map = {}
        legislators = db.query(Legislator.id, Legislator.hg_nm).all()
        for leg_id, leg_name in legislators:
            legislator_map[leg_name] = leg_id
        
        print(f"의원 매핑 생성 완료: {len(legislator_map)}명")
        
        # 기존 발언 데이터 삭제 (중복 방지)
        deleted_count = db.query(SpeechByMeeting).delete()
        print(f"기존 발언 데이터 삭제: {deleted_count}개")
        
        # 새 데이터 추가
        added_count = 0
        for item in raw_data:
            legislator_name = item['legislator_name']
            meeting_type = item['meeting_type']
            count = item['count']
            
            legislator_id = legislator_map.get(legislator_name)
            if legislator_id:
                speech = SpeechByMeeting(
                    legislator_id=legislator_id,
                    meeting_type=meeting_type,
                    count=count
                )
                db.add(speech)
                added_count += 1
            else:
                print(f"의원을 찾을 수 없음: {legislator_name}")
        
        # 변경사항 커밋
        if added_count > 0:
            db.commit()
            print(f"{added_count}개의 발언 데이터 저장 완료")
        
        return raw_data
    
    except Exception as e:
        db.rollback()
        print(f"발언 데이터 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        if should_close_db:
            db.close()

def process_bill_data(raw_data):
    # 법안 데이터 정리 및 가공
    # 대표발의, 공동발의 구분
    # 반환: 처리된 법안 데이터
    pass

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