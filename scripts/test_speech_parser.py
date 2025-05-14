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
from app.utils.excel_parser import parse_speech_by_meeting_excel
from app.db.database import SessionLocal
from app.services.data_processing import process_speech_data

def test_parse_speech_by_meeting():
    """
    회의별 발언 엑셀 파일 파싱 테스트
    """
    # 테스트 파일 경로 설정
    speech_by_meeting_dir = "data/excel/speech/speech_by_meeting"
    
    if not os.path.exists(speech_by_meeting_dir):
        print(f"폴더가 존재하지 않습니다: {speech_by_meeting_dir}")
        return
    
    # 첫 번째 파일만 테스트
    files = os.listdir(speech_by_meeting_dir)
    if not files:
        print("테스트할 파일이 없습니다.")
        return
    
    test_file = None
    for file in files:
        if file.endswith("_speech_by_meeting.xlsx"):
            test_file = os.path.join(speech_by_meeting_dir, file)
            break
    
    if not test_file:
        print("테스트할 파일을 찾을 수 없습니다.")
        return
    
    print(f"테스트 파일: {test_file}")
    
    # 파일 파싱 테스트
    speech_data = parse_speech_by_meeting_excel(test_file)
    
    # 결과 출력
    print(f"파싱 결과: {len(speech_data)}개의 데이터")
    
    # 첫 5개 데이터 출력
    for i, data in enumerate(speech_data[:5]):
        print(f"{i+1}. {data['legislator_name']} - {data['meeting_type']}: {data['count']}회")
    
    # DB 저장 테스트 (선택 사항)
    test_db_save = input("DB 저장 테스트를 진행하시겠습니까? (y/n): ")
    if test_db_save.lower() == 'y':
        try:
            print("\nDB에서 의원 정보 확인 중...")
            db = SessionLocal()
            try:
                # DB에 의원 정보가 있는지 먼저 확인
                name = speech_data[0]['legislator_name'] if speech_data else None
                if name:
                    legislator = db.query(Legislator).filter(Legislator.hg_nm == name).first()
                    if legislator:
                        print(f"의원 정보 확인됨: {legislator.hg_nm}")
                    else:
                        print(f"경고: {name} 의원 정보가 DB에 없습니다.")
                        print("fetch_data.py를 먼저 실행해서 의원 정보를 수집해주세요.")
                        return
                
                process_speech_data(speech_data, db)
                print("DB 저장 테스트 완료")
            finally:
                db.close()
        except Exception as e:
            print(f"DB 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_parse_speech_by_meeting()