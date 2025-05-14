import sys
import os

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

# 그 다음에 나머지 import
from app.db.database import SessionLocal

def check_speech_data():
    """DB에 저장된 발언 데이터 확인"""
    db = SessionLocal()
    try:
        # 강경숙 의원 정보 조회
        legislator = db.query(Legislator).filter(Legislator.hg_nm == "강경숙").first()
        if not legislator:
            print("강경숙 의원 정보를 찾을 수 없습니다.")
            return
        
        print(f"의원: {legislator.hg_nm} (ID: {legislator.id})")
        
        # 발언 데이터 조회
        speeches = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.legislator_id == legislator.id
        ).all()
        
        print(f"\n발언 데이터 ({len(speeches)}개):")
        for speech in speeches:
            print(f"- {speech.meeting_type}: {speech.count}회")
        
        # Total 값 확인
        total_speech = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.legislator_id == legislator.id,
            SpeechByMeeting.meeting_type == "Total"
        ).first()
        
        if total_speech:
            print(f"\nTotal 발언수: {total_speech.count}")
        else:
            print("\nTotal 발언수가 없습니다.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_speech_data()