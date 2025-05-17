#!/usr/bin/env python3
import sys
import os
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
# 모든 모델을 명시적으로 임포트
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def reset_scores(db: Session = None):
    """
    모든 의원의 점수를 초기화하는 함수
    
    Args:
        db: 데이터베이스 세션 (None인 경우 새로 생성)
    """
    close_db = False
    
    try:
        if db is None:
            db = SessionLocal()
            close_db = True
        
        print("모든 의원의 점수를 초기화합니다...")
        
        # 모든 의원의 점수 NULL로 초기화
        result = db.query(Legislator).update({
            Legislator.participation_score: None,
            Legislator.legislation_score: None,
            Legislator.speech_score: None,
            Legislator.voting_score: None,
            Legislator.cooperation_score: None,
            Legislator.overall_score: None,
            Legislator.tier: None,
            Legislator.overall_rank: None
        })
        
        db.commit()
        print(f"초기화 완료: {result}명의 의원 점수가 초기화되었습니다.")
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"점수 초기화 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if close_db and db:
            db.close()
    
    return True

if __name__ == "__main__":
    # 명령줄 인자 처리
    import argparse
    
    parser = argparse.ArgumentParser(description="의원 점수 초기화 스크립트")
    parser.add_argument('--confirm', action='store_true', help="초기화 확인 없이 진행")
    args = parser.parse_args()
    
    # 확인 메시지 출력
    if not args.confirm:
        confirm = input("모든 의원의 점수를 초기화합니다. 계속하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("작업이 취소되었습니다.")
            sys.exit(0)
    
    # 점수 초기화 실행
    success = reset_scores()
    
    # 종료 코드 설정
    sys.exit(0 if success else 1)