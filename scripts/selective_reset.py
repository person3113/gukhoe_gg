import sys
import os
from sqlalchemy import inspect, text

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base, SessionLocal
from app.models.legislator import Legislator
from app.models.bill import Bill, BillCoProposer
from app.models.committee import Committee, CommitteeMember, CommitteeHistory
from app.models.vote import Vote, VoteResult
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.sns import LegislatorSNS

def reset_selected_tables(preserve_legislators=True, preserve_bills=False):
    """
    선택적 테이블 초기화
    
    Args:
        preserve_legislators: 국회의원 정보를 보존할지 여부 (기본: True)
        preserve_bills: 법안 정보를 보존할지 여부 (기본: False)
    """
    db = SessionLocal()
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    try:
        print("선택적 테이블 초기화를 시작합니다...")
        
        # 삭제할 테이블 목록 (순서 중요 - 외래 키 관계 고려)
        tables_to_reset = [
            # 의원 정보와 관련 없는 테이블 또는 의원 정보에 의존하는 테이블
            VoteResult.__tablename__,  # 표결 결과
            Vote.__tablename__,  # 표결
            Attendance.__tablename__,  # 출석
            SpeechKeyword.__tablename__,  # 발언 키워드
            SpeechByMeeting.__tablename__,  # 회의별 발언
            CommitteeMember.__tablename__,  # 위원회 멤버십
            CommitteeHistory.__tablename__,  # 위원회 경력
            Committee.__tablename__,  # 위원회
        ]
        
        # 법안 정보를 보존하지 않을 경우 법안 관련 테이블도 초기화 대상에 추가
        if not preserve_bills:
            tables_to_reset.append(BillCoProposer.__tablename__)  # 법안 공동발의자
            tables_to_reset.append(Bill.__tablename__)  # 법안
        
        # 국회의원 정보도 초기화하려면 LegislatorSNS와 Legislator 테이블도 포함
        if not preserve_legislators:
            tables_to_reset.append(LegislatorSNS.__tablename__)
            tables_to_reset.append(Legislator.__tablename__)
        
        # 테이블별로 데이터 삭제
        for table_name in tables_to_reset:
            if table_name in existing_tables:
                print(f"{table_name} 테이블의 데이터를 삭제합니다...")
                db.execute(text(f"DELETE FROM {table_name}"))
        
        # 변경사항 커밋
        db.commit()
        print("선택적 테이블 초기화가 완료되었습니다.")
        
        # 보존된 정보 출력
        if preserve_legislators:
            legislator_count = db.query(Legislator).count()
            print(f"국회의원 정보 {legislator_count}건이 보존되었습니다.")
        
        if preserve_bills:
            bill_count = db.query(Bill).count()
            co_proposer_count = db.query(BillCoProposer).count()
            print(f"법안 정보 {bill_count}건과 공동발의자 정보 {co_proposer_count}건이 보존되었습니다.")
    
    except Exception as e:
        print(f"초기화 중 오류가 발생했습니다: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 사용자 입력에 따라 동작 결정
    print("선택적 테이블 초기화 스크립트")
    print("1. 국회의원 정보는 유지하고 다른 테이블만 초기화")
    print("2. 국회의원 정보와 법안 정보는 유지하고 다른 테이블만 초기화")
    print("3. 모든 테이블 초기화 (기존 reset_db.py와 동일)")
    
    choice = input("선택하세요 (1, 2 또는 3): ")
    
    if choice == '1':
        reset_selected_tables(preserve_legislators=True, preserve_bills=False)
    elif choice == '2':
        reset_selected_tables(preserve_legislators=True, preserve_bills=True)
    elif choice == '3':
        reset_selected_tables(preserve_legislators=False, preserve_bills=False)
    else:
        print("잘못된 선택입니다. 작업이 취소되었습니다.")