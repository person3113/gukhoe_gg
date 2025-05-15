from sqlalchemy.orm import Session
from typing import List, Dict, Any
from scripts.calculate_scores import calculate_participation_scores

def process_attendance_data(raw_data: List[Dict[str, Any]], db: Session) -> None:
    # 출석 데이터 정리 및 가공
    # 출석률 계산
    # 반환: 처리된 출석 데이터
    """
    출석 데이터 처리 및 DB 저장
    
    Args:
        raw_data: 출석 데이터 리스트
        db: 데이터베이스 세션
    """
    from app.models.attendance import Attendance
    from app.models.legislator import Legislator
    from app.models.committee import Committee
    
    try:
        processed_count = 0
        skipped_count = 0
        updated_count = 0
        
        # 의원 이름 캐시 및 위원회 이름 캐시
        legislator_name_map = {}
        committee_name_map = {}
        
        # 각 출석 데이터 처리
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
            
            # 위원회 정보 처리 (상임위인 경우)
            committee_id = None
            if data['meeting_type'] == '상임위' and 'committee_name' in data and data['committee_name']:
                committee_name = data['committee_name']
                
                # 위원회 정보가 캐시에 없으면 DB에서 조회
                if committee_name not in committee_name_map:
                    committee = db.query(Committee).filter(Committee.dept_nm == committee_name).first()
                    if committee:
                        committee_name_map[committee_name] = committee
                    else:
                        print(f"경고: {committee_name} 위원회를 DB에서 찾을 수 없습니다.")
                        committee_name_map[committee_name] = None
                
                committee = committee_name_map[committee_name]
                if committee:
                    committee_id = committee.id
            
            # 기존 출석 데이터 확인
            existing_attendance = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_date == data['meeting_date'],
                Attendance.meeting_type == data['meeting_type']
            ).first()
            
            if existing_attendance:
                # 기존 데이터가 있으면 업데이트 여부 결정
                if existing_attendance.status != data['status']:
                    print(f"출석 상태 업데이트: {legislator.hg_nm}, {data['meeting_date']}, {data['meeting_type']}: {existing_attendance.status} -> {data['status']}")
                    existing_attendance.status = data['status']
                    updated_count += 1
                else:
                    print(f"동일한 출석 데이터 건너뜀: {legislator.hg_nm}, {data['meeting_date']}, {data['meeting_type']}: {data['status']}")
            else:
                # 새 출석 데이터 추가
                new_attendance = Attendance(
                    legislator_id=legislator.id,
                    committee_id=committee_id,
                    meeting_date=data['meeting_date'],
                    meeting_type=data['meeting_type'],
                    status=data['status']
                )
                db.add(new_attendance)
                print(f"새 출석 데이터 추가: {legislator.hg_nm}, {data['meeting_date']}, {data['meeting_type']}: {data['status']}")
                processed_count += 1
        
        # 변경사항 커밋
        db.commit()
        print(f"\n=== 출석 데이터 처리 결과 ===")
        print(f"새로 추가: {processed_count}개")
        print(f"업데이트: {updated_count}개")
        print(f"건너뜀: {skipped_count}개")
        
        # 출석 데이터가 추가되었으면 참여 점수 재계산
        if processed_count > 0 or updated_count > 0:
            # 함수 내부에서 직접 임포트
            import sys
            import os
            # 프로젝트 루트 디렉토리 추가 (상대 경로 문제 해결)
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
            from scripts.calculate_scores import calculate_participation_scores
            # 여기서 동일한 db 세션 전달
            participation_db = db  # 명시적인 할당으로 변수명 변경
            calculate_participation_scores(participation_db)
        
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