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
        # 전체 의원 조회
        legislators = db.query(Legislator).all()
        print(f"총 {len(legislators)}명의 의원 데이터")
        
        # 발언 데이터가 있는 의원과 없는 의원 구분
        legislators_with_data = []
        legislators_without_data = []
        
        for legislator in legislators:
            # 발언 데이터 조회
            speeches = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id
            ).all()
            
            if speeches:
                legislators_with_data.append((legislator, speeches))
            else:
                legislators_without_data.append(legislator)
        
        print(f"\n발언 데이터가 있는 의원: {len(legislators_with_data)}명")
        print(f"발언 데이터가 없는 의원: {len(legislators_without_data)}명")
        
        # 발언 데이터가 있는 의원들의 상세 정보
        print("\n=== 발언 데이터가 있는 의원 목록 ===")
        for i, (legislator, speeches) in enumerate(legislators_with_data[:10], 1):  # 처음 10명만 표시
            print(f"\n{i}. {legislator.hg_nm} (ID: {legislator.id})")
            
            # Total 값 확인
            total_speech = next((s for s in speeches if s.meeting_type == "Total"), None)
            if total_speech:
                print(f"   Total: {total_speech.count}회")
            else:
                print("   Total: 없음")
            
            # speech_score 확인
            print(f"   speech_score: {legislator.speech_score}")
            
            # 각 회의별 발언수 (상세)
            print("   회의별 발언수:")
            for speech in speeches:
                if speech.meeting_type != "Total":
                    print(f"     - {speech.meeting_type}: {speech.count}회")
        
        # 발언 데이터가 없는 의원들 이름 출력
        print("\n=== 발언 데이터가 없는 의원 목록 ===")
        for i, legislator in enumerate(legislators_without_data[:20], 1):  # 처음 20명만 표시
            print(f"{i}. {legislator.hg_nm} (ID: {legislator.id})")
        
        # 통계 정보
        print("\n=== 통계 정보 ===")
        
        # speech_score가 0이 아닌 의원 수
        legislators_with_score = db.query(Legislator).filter(
            Legislator.speech_score != 0,
            Legislator.speech_score != None
        ).count()
        
        print(f"speech_score가 있는 의원: {legislators_with_score}명")
        
        # Total이 있는 의원 수
        total_count = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.meeting_type == "Total"
        ).distinct(SpeechByMeeting.legislator_id).count()
        
        print(f"Total 데이터가 있는 의원: {total_count}명")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_speech_data()