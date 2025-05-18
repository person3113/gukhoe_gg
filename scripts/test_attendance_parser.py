import sys
import os
import traceback
from sqlalchemy import func

print("테스트 스크립트 시작...")
print(f"현재 작업 디렉토리: {os.getcwd()}")

# 프로젝트 루트 디렉토리 추가
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    print("프로젝트 루트 디렉토리 추가 성공")
except Exception as e:
    print(f"프로젝트 루트 디렉토리 추가 실패: {e}")
    traceback.print_exc()

# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
try:
    from app.models.legislator import Legislator
    print("Legislator 모델 임포트 성공")
except Exception as e:
    print(f"Legislator 모델 임포트 실패: {e}")
    traceback.print_exc()

try:
    from app.models.sns import LegislatorSNS
    from app.models.committee import Committee, CommitteeHistory, CommitteeMember
    from app.models.speech import SpeechKeyword, SpeechByMeeting
    from app.models.attendance import Attendance
    from app.models.bill import Bill, BillCoProposer
    from app.models.vote import Vote, VoteResult
    print("나머지 모델 임포트 성공")
except Exception as e:
    print(f"나머지 모델 임포트 실패: {e}")
    traceback.print_exc()

# 그 다음에 나머지 import
try:
    from app.utils.excel_parser import parse_attendance_excel
    print("parse_attendance_excel 함수 임포트 성공")
except Exception as e:
    print(f"parse_attendance_excel 함수 임포트 실패: {e}")
    traceback.print_exc()

try:
    from app.db.database import SessionLocal
    print("SessionLocal 임포트 성공")
except Exception as e:
    print(f"SessionLocal 임포트 실패: {e}")
    traceback.print_exc()

try:
    from app.services.data_processing import process_attendance_data
    print("process_attendance_data 함수 임포트 성공")
except Exception as e:
    print(f"process_attendance_data 함수 임포트 실패: {e}")
    traceback.print_exc()

print("모듈 임포트 완료. 테스트 함수 시작...")

def test_parse_attendance_excel():
    """
    출석 현황 엑셀 파일 파싱 테스트
    """
    print("테스트 함수 내부 진입...")
    
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
        print("테스트할 파일이 없습니다. 데이터 폴더를 확인해주세요.")
        # 폴더 생성 제안
        print("다음 폴더가 있는지 확인하세요:")
        for dir_path in attendance_dirs:
            print(f"  - {dir_path}")
        return
    
    print(f"총 {len(all_files)}개의 파일을 테스트합니다.")
    
    # 각 파일 테스트
    for file_path in all_files:
        filename = os.path.basename(file_path)
        print(f"\n테스트 파일: {filename}")
        
        # 파일 타입 확인
        if '/plenary/' in file_path or '\\plenary\\' in file_path or '_plenary_' in filename.lower():
            print("  - 파일 타입: 본회의 출석")
        else:
            print("  - 파일 타입: 상임위 출석")
        
        # 파일 파싱 테스트
        try:
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
                
                # 의원별로 그룹화
                legislator_summary = {}
                for data in attendance_data:
                    name = data['legislator_name']
                    if name not in legislator_summary:
                        legislator_summary[name] = 0
                    legislator_summary[name] += 1
                
                print(f"\n  - 파싱된 의원 수: {len(legislator_summary)}명")
                
                # 샘플 데이터 출력
                print("\n  - 데이터 샘플 (첫 5개):")
                for i, data in enumerate(attendance_data[:5]):
                    print(f"    {i+1}. {data['legislator_name']} - {data['meeting_type']} - {data['status']}: {data.get('count', 0)}")
        except Exception as e:
            print(f"  - 파일 파싱 중 오류 발생: {e}")
            traceback.print_exc()
    
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
                
                 # 기존 출석 데이터 초기화 (추가된 부분)
                deleted_count = db.query(Attendance).delete()
                db.commit()
                print(f"\n기존 출석 데이터 {deleted_count}개를 초기화했습니다.")
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

                # 1. 몇 개의 샘플 출석 데이터 확인
                test_result = db.query(Attendance).filter(
                    Attendance.count > 0
                ).limit(5).all()

                print("\n1. 샘플 출석 데이터:")
                for i, attendance in enumerate(test_result, 1):
                    legislator = db.query(Legislator).filter(
                        Legislator.id == attendance.legislator_id
                    ).first()
                    print(f"{i}. {legislator.hg_nm} - {attendance.meeting_type} - {attendance.status}: {attendance.count}")

                # 2. 상임위 전체 카운트 (상태별)
                print("\n2. 상임위 전체 카운트 (상태별):")
                statuses = ["회의일수", "출석", "결석", "청가", "출장", "결석신고서"]

                for status in statuses:
                    total_count = db.query(func.sum(Attendance.count)).filter(
                        Attendance.meeting_type == "상임위",
                        Attendance.status == status
                    ).scalar()
                    
                    # None이면 0으로 처리
                    total_count = total_count or 0
                    
                    print(f"   {status}: {total_count}회")

                # 3. 몇 명의 의원에 대한 상임위 상태별 카운트 상세 확인
                print("\n3. 의원별 상임위 출석 상태 (5명 샘플):")
                legislators = db.query(Legislator).limit(5).all()

                for legislator in legislators:
                    print(f"\n  • {legislator.hg_nm} 의원:")
                    
                    for status in statuses:
                        attendance_record = db.query(Attendance).filter(
                            Attendance.legislator_id == legislator.id,
                            Attendance.meeting_type == "상임위",
                            Attendance.status == status
                        ).first()
                        
                        count = attendance_record.count if attendance_record else 0
                        print(f"     - {status}: {count}회")

                print("\nDB 저장 테스트 완료")
            finally:
                db.close()
        except Exception as e:
            print(f"DB 저장 중 오류 발생: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        print("test_parse_attendance_excel 함수 호출 시작...")
        test_parse_attendance_excel()
        print("테스트 완료!")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        traceback.print_exc()