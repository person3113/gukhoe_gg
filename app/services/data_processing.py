from sqlalchemy.orm import Session

def process_attendance_data(raw_data):
    # 출석 데이터 정리 및 가공
    # 출석률 계산
    # 반환: 처리된 출석 데이터
    pass

def process_speech_data(raw_data):
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
    if not raw_data:
        return []
    
    result = []
    
    if type == "keywords":
        # 키워드 데이터 처리 로직...
        pass
    
    elif type == "by_meeting":
        # 회의별 발언 데이터 처리
        for item in raw_data:
            legislator_name = item.get("legislator_name")
            meeting_type = item.get("meeting_type")
            count = item.get("count", 0)
            
            # 데이터 검증
            if not legislator_name or not meeting_type:
                continue
            
            # 결과에 추가 (Total 포함)
            result.append({
                "legislator_name": legislator_name,
                "meeting_type": meeting_type,
                "count": count
            })
    
    return result

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