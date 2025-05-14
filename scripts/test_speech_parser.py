import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        db = SessionLocal()
        try:
            process_speech_data(speech_data, db)
            print("DB 저장 테스트 완료")
        finally:
            db.close()

if __name__ == "__main__":
    test_parse_speech_by_meeting()