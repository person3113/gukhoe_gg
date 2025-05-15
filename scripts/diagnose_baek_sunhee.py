import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.excel_parser import parse_speech_by_meeting_excel
from app.db.database import SessionLocal
from app.models.legislator import Legislator
from app.models.speech import SpeechByMeeting

from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def diagnose_baek_sunhee():
    """백선희 의원 데이터 문제 진단"""
    db = SessionLocal()
    try:
        print("=== 백선희 의원 데이터 진단 ===")
        
        # 1. DB에서 백선희 의원 찾기
        legislator = db.query(Legislator).filter(Legislator.hg_nm == "백선희").first()
        if not legislator:
            print("DB에 백선희 의원이 없습니다!")
            return
        
        print(f"1. DB에서 찾음: {legislator.hg_nm} (ID: {legislator.id})")
        
        # 2. 발언 데이터 확인
        speeches = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.legislator_id == legislator.id
        ).all()
        
        print(f"2. 발언 데이터: {len(speeches)}개")
        for speech in speeches:
            print(f"   - {speech.meeting_type}: {speech.count}")
        
        # 3. 엑셀 파일 존재 확인
        file_path = "data/excel/speech/speech_by_meeting/백선희_speech_by_meeting.xlsx"
        print(f"\n3. 엑셀 파일 존재: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            # 4. 파일 직접 파싱
            print("\n4. 파일 파싱 테스트:")
            parsed_data = parse_speech_by_meeting_excel(file_path)
            print(f"   파싱된 데이터: {len(parsed_data)}개")
            
            # 파싱된 데이터 중 백선희 의원 데이터만 필터
            baek_data = [d for d in parsed_data if d['legislator_name'] == '백선희']
            print(f"   백선희 의원 데이터: {len(baek_data)}개")
            
            for data in baek_data[:5]:  # 처음 5개만
                print(f"     - {data['meeting_type']}: {data['count']} (대수: {data['assembly_no']})")
        
        # 5. 비슷한 이름 검색
        print("\n5. 비슷한 이름 검색:")
        similar = db.query(Legislator).filter(
            Legislator.hg_nm.like("%백%")
        ).all()
        
        for s in similar:
            print(f"   - {s.hg_nm} (ID: {s.id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_baek_sunhee()