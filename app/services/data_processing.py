from sqlalchemy.orm import Session
from typing import List, Dict, Any

def process_attendance_data(raw_data):
    # 출석 데이터 정리 및 가공
    # 출석률 계산
    # 반환: 처리된 출석 데이터
    pass

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
        
        # 각 발언 데이터를 처리
        for data in raw_data:
            # 의원 이름으로 의원 ID 조회
            legislator = db.query(Legislator).filter(Legislator.hg_nm == data['legislator_name']).first()
            
            if not legislator:
                print(f"의원을 찾을 수 없음: {data['legislator_name']}")
                continue
                
            # 'Total'은 따로 저장해두고, speech_score 계산에 사용
            if data['meeting_type'] == 'Total':
                total_speeches[legislator.id] = data['count']
                
                # 의원의 speech_score 필드가 있으면 업데이트 (Total 값 기반 점수 계산)
                if hasattr(legislator, 'speech_score'):
                    # 추후 계산 로직이 필요할 경우 추가
                    pass
                
                # Total 데이터도 DB에 저장
                existing_speech = db.query(SpeechByMeeting).filter(
                    SpeechByMeeting.legislator_id == legislator.id,
                    SpeechByMeeting.meeting_type == 'Total'
                ).first()
                
                if existing_speech:
                    # 기존 데이터 업데이트
                    existing_speech.count = data['count']
                else:
                    # 새 데이터 추가
                    new_speech = SpeechByMeeting(
                        legislator_id=legislator.id,
                        meeting_type='Total',
                        count=data['count']
                    )
                    db.add(new_speech)
                
                continue
            
            # 일반 회의 구분별 발언 수는 SpeechByMeeting 테이블에 저장
            existing_speech = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id,
                SpeechByMeeting.meeting_type == data['meeting_type']
            ).first()
            
            if existing_speech:
                # 기존 데이터 업데이트
                existing_speech.count = data['count']
            else:
                # 새 데이터 추가
                new_speech = SpeechByMeeting(
                    legislator_id=legislator.id,
                    meeting_type=data['meeting_type'],
                    count=data['count']
                )
                db.add(new_speech)
        
        # 변경사항 커밋
        db.commit()
        print(f"{len(raw_data)}개의 발언 데이터 처리 완료 (Total 포함)")
        
        # 추가 정보 출력
        print(f"의원별 Total 발언 수: {len(total_speeches)}명")
        
    except Exception as e:
        db.rollback()
        print(f"발언 데이터 처리 오류: {str(e)}")
        import traceback
        traceback.print_exc()

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