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
from app.utils.excel_parser import parse_attendance_excel  # 기존 함수명 유지
from app.db.database import SessionLocal
from app.services.data_processing import process_attendance_data

def test_parse_attendance_excel():
    """
    출석 현황 엑셀 파일 파싱 테스트
    """
    # 테스트 파일 경로 설정
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
        print("테스트할 파일이 없습니다.")
        return
    
    # 각 파일 테스트
    for file_path in all_files:
        filename = os.path.basename(file_path)
        print(f"\n테스트 파일: {filename}")
        
        # 파일 타입 확인
        if 'plenary' in file_path:
            print("  - 파일 타입: 본회의 출석")
        else:
            print("  - 파일 타입: 상임위 출석")
        
        # 파일 파싱 테스트
        attendance_data = parse_attendance_excel(file_path)
        
        # 결과 출력
        print(f"  - 파싱 결과: {len(attendance_data)}개의 출석 데이터")
        
        # 데이터 요약 출력
        if attendance_data:
            # 상태별로 그룹화
            status_summary = {}
            for data in attendance_data:
                status = data['status']
                if status not in status_summary:
                    status_summary[status] = 0
                status_summary[status] += 1
            
            print("\n  - 상태별 데이터 수:")
            for status, count in status_summary.items():
                print(f"    {status}: {count}개")
            
            # 샘플 데이터 출력
            print("\n  - 데이터 샘플 (첫 5개):")
            for i, data in enumerate(attendance_data[:5]):
                print(f"    {i+1}. {data['legislator_name']} - {data['meeting_type']} - {data['status']}: {data.get('count', 0)}")
    
    # DB 저장 테스트
    test_db_save = input("\nDB 저장 테스트를 진행하시겠습니까? (y/n): ")
    if test_db_save.lower() == 'y':
        try:
            db = SessionLocal()
            try:
                # DB에 의원 정보가 있는지 확인
                legislator_count = db.query(Legislator).count()
                if legislator_count == 0:
                    print("경고: DB에 의원 정보가 없습니다.")
                    print("fetch_data.py를 먼저 실행해서 의원 정보를 수집해주세요.")
                    return
                
                print(f"DB에 {legislator_count}명의 의원 정보가 있습니다.")
                
                # 모든 파일의 데이터를 수집
                all_attendance_data = []
                for file_path in all_files:
                    attendance_data = parse_attendance_excel(file_path)
                    all_attendance_data.extend(attendance_data)
                
                print(f"\n총 {len(all_attendance_data)}개의 출석 데이터 처리 중...")
                
                # 출석 데이터 처리 및 DB 저장
                process_attendance_data(all_attendance_data, db)
                
                # 저장 후 데이터 확인
                test_result = db.query(Attendance).filter(
                    Attendance.count > 0
                ).limit(5).all()
                
                print("\n=== DB 저장 확인 ===")
                for i, attendance in enumerate(test_result, 1):
                    legislator = db.query(Legislator).filter(
                        Legislator.id == attendance.legislator_id
                    ).first()
                    print(f"{i}. {legislator.hg_nm} - {attendance.meeting_type} - {attendance.status}: {attendance.count}")
                
                print("\nDB 저장 테스트 완료")
            finally:
                db.close()
        except Exception as e:
            print(f"DB 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_parse_attendance_excel()