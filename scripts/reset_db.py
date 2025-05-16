import sys
import os
import argparse

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

# DB 관련 import
from app.db.database import engine, Base, SessionLocal

def reset_database(confirm=False):
    """
    데이터베이스를 초기화합니다. 모든 테이블을 삭제하고 다시 생성합니다.
    
    Args:
        confirm: 사용자 확인 없이 진행할지 여부
    """
    if not confirm:
        response = input("모든 데이터베이스 테이블이 삭제되고 다시 생성됩니다. 계속하시겠습니까? (yes/no): ")
        if response.lower() != 'yes':
            print("데이터베이스 초기화가 취소되었습니다.")
            return
    
    try:
        print("데이터베이스 초기화 시작...")
        
        # 모든 테이블 삭제
        print("기존 테이블 삭제 중...")
        Base.metadata.drop_all(bind=engine)
        
        # 테이블 다시 생성
        print("테이블 재생성 중...")
        Base.metadata.create_all(bind=engine)
        
        print("데이터베이스 초기화가 완료되었습니다.")
        
        # 초기 데이터 생성 여부 확인
        if not confirm:  # 대화형 모드일 때만 물어봄
            create_dummy = input("더미 데이터를 생성하시겠습니까? (yes/no): ")
            if create_dummy.lower() == 'yes':
                try:
                    from scripts.create_dummy_data import create_dummy_data
                    create_dummy_data()
                    print("더미 데이터가 생성되었습니다.")
                except Exception as e:
                    print(f"더미 데이터 생성 중 오류가 발생했습니다: {e}")
    
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='데이터베이스 초기화 스크립트')
    parser.add_argument('--force', action='store_true', help='확인 없이 강제로 초기화')
    parser.add_argument('--dummy', action='store_true', help='더미 데이터 자동 생성')
    
    args = parser.parse_args()
    
    # 데이터베이스 초기화
    reset_database(confirm=args.force)
    
    # 더미 데이터 자동 생성 옵션 처리
    if args.dummy and args.force:  # --force와 함께 사용된 경우에만
        try:
            from scripts.create_dummy_data import create_dummy_data
            create_dummy_data()
            print("더미 데이터가 생성되었습니다.")
        except Exception as e:
            print(f"더미 데이터 생성 중 오류가 발생했습니다: {e}")