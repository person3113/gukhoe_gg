
import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
from app.models.legislator import Legislator
from app.models.speech import SpeechByMeeting

from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

from app.db.database import SessionLocal

def reset_speech_data():
    """모든 발언 데이터 삭제"""
    db = SessionLocal()
    try:
        # 모든 발언 데이터 삭제
        deleted_count = db.query(SpeechByMeeting).delete()
        db.commit()
        print(f"삭제된 발언 데이터: {deleted_count}개")
        
        # 모든 의원의 speech_score를 0으로 초기화
        legislators = db.query(Legislator).all()
        for legislator in legislators:
            legislator.speech_score = 0
        db.commit()
        print(f"{len(legislators)}명의 speech_score를 0으로 초기화했습니다.")
        
        # 확인
        remaining = db.query(SpeechByMeeting).count()
        print(f"남은 발언 데이터: {remaining}개")
        
    except Exception as e:
        db.rollback()
        print(f"데이터 삭제 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    response = input("정말로 모든 발언 데이터를 삭제하시겠습니까? (yes/no): ")
    if response.lower() == 'yes':
        reset_speech_data()
    else:
        print("취소되었습니다.")