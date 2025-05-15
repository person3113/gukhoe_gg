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
from app.utils.excel_parser import parse_attendance_excel
from app.db.database import SessionLocal
from app.services.data_processing import process_attendance_data

def test_parse_attendance_excel():
    """
    출석 현황 엑셀 파일 파싱 테스트
    """
    # 테스트 파일 경로 설정 - 하나는 본회의, 하나는 상임위
    attendance_dirs = [
        "data/excel/attendance/plenary",
        "data/excel/attendance/standing_committee"
    ]
    
    all_files = []
    for attendance_dir in attendance_dirs:
        if not os.path.exists(attendance_dir):
            print(f"폴더가 존재하지 않습니다: {attendance_dir}")
            continue
        
        # 폴더 내 엑셀 파일 목록
        files = [f for f in os.listdir(attendance_dir) if f.endswith('.xlsx')]
        for file in files:
            all_files.append(os.path.join(attendance_dir, file))
    
    if not all_files:
        print("테스트할 파일이 없습니다. 출석 현황 엑셀 파일을 해당 폴더에 먼저 넣어주세요.")
        return
    
    # 각 파일 테스트
    for file_path in all_files:
        filename = os.path.basename(file_path)
        print(f"\n테스트 파일: {filename}")
        
        # 파일 파싱 테스트
        attendance_data = parse_attendance_excel(file_path)
        
        # 결과 출력
        print(f"파싱 결과: {len(attendance_data)}개의 출석 데이터")
        
        # 첫 5개 데이터 출력
        print("\n첫 5개 출석 데이터 샘플:")
        for i, data in enumerate(attendance_data[:5]):
            print(f"{i+1}. {data['legislator_name']} - {data['meeting_date']} - {data['meeting_type']} - {data['status']}")
        
        # DB 저장 테스트
        test_db_save = input(f"\n{filename} 파일의 DB 저장 테스트를 진행하시겠습니까? (y/n): ")
        if test_db_save.lower() == 'y':
            try:
                print("\nDB에서 의원 정보 확인 중...")
                db = SessionLocal()
                try:
                    # DB에 의원 정보가 있는지 먼저 확인
                    legislator_count = db.query(Legislator).count()
                    if legislator_count == 0:
                        print("경고: DB에 의원 정보가 없습니다.")
                        print("fetch_data.py를 먼저 실행해서 의원 정보를 수집해주세요.")
                        return
                    
                    print(f"DB에 {legislator_count}명의 의원 정보가 있습니다.")
                    print("\n출석 데이터 DB 저장 테스트 시작...")
                    
                    # 출석 데이터 처리 및 DB 저장
                    process_attendance_data(attendance_data, db)
                    
                    # 저장 후 데이터 확인
                    attendance_count = db.query(Attendance).count()
                    print(f"\n현재 DB의 총 출석 데이터 수: {attendance_count}개")
                    
                    print("DB 저장 테스트 완료")
                finally:
                    db.close()
            except Exception as e:
                print(f"DB 저장 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_parse_attendance_excel()