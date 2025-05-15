import sys
import os
import glob

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.models.legislator import Legislator


# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult
def check_file_name_matching():
    """엑셀 파일명과 DB 의원명 매칭 확인"""
    db = SessionLocal()
    try:
        # 엑셀 파일 목록 가져오기
        speech_by_meeting_dir = "data/excel/speech/speech_by_meeting"
        files = glob.glob(os.path.join(speech_by_meeting_dir, "*_speech_by_meeting.xlsx"))
        
        print(f"총 {len(files)}개의 파일 발견")
        
        # DB의 모든 의원 이름 가져오기
        legislators = db.query(Legislator).all()
        db_names = {leg.hg_nm: leg.id for leg in legislators}
        
        print(f"DB에는 {len(db_names)}명의 의원이 있습니다.")
        
        # 매칭 실패한 파일들
        unmatched_files = []
        matched_count = 0
        
        print("\n=== 파일명 매칭 확인 ===")
        for file_path in files:
            filename = os.path.basename(file_path)
            # 파일명에서 의원 이름 추출
            name_from_file = filename.replace("_speech_by_meeting.xlsx", "")
            
            # DB에서 찾기 (정확한 매칭)
            if name_from_file in db_names:
                matched_count += 1
            else:
                # 공백 제거 후 다시 시도
                name_no_space = name_from_file.replace(" ", "")
                name_with_space = name_from_file.replace("", " ")  # 이건 의미없음
                
                found = False
                # 다양한 방법으로 매칭 시도
                for db_name in db_names:
                    if (db_name.replace(" ", "") == name_no_space or 
                        db_name == name_no_space or
                        name_from_file.replace(" ", "") == db_name.replace(" ", "")):
                        print(f"매칭 성공 (공백 차이): '{name_from_file}' -> '{db_name}'")
                        matched_count += 1
                        found = True
                        break
                
                if not found:
                    unmatched_files.append(name_from_file)
                    print(f"매칭 실패: '{name_from_file}'")
        
        print(f"\n=== 매칭 결과 ===")
        print(f"매칭 성공: {matched_count}개")
        print(f"매칭 실패: {len(unmatched_files)}개")
        
        if unmatched_files:
            print("\n=== 매칭 실패한 파일들 ===")
            for name in unmatched_files[:20]:  # 처음 20개만 표시
                print(f"- {name}")
                # DB에서 비슷한 이름 찾기
                similar = []
                for db_name in db_names:
                    if name.replace(" ", "") in db_name.replace(" ", "") or db_name.replace(" ", "") in name.replace(" ", ""):
                        similar.append(db_name)
                if similar:
                    print(f"  비슷한 이름: {similar}")
        
        # 발언 데이터가 없는 의원들의 이름과 파일 존재 여부 확인
        print("\n=== 발언 데이터가 없는 의원들 ===")
        for legislator in legislators:
            if not db.query(SpeechByMeeting).filter(SpeechByMeeting.legislator_id == legislator.id).first():
                print(f"{legislator.hg_nm} (ID: {legislator.id})")
                # 이 의원의 파일이 있는지 확인
                found_file = False
                for file_path in files:
                    filename = os.path.basename(file_path)
                    name_from_file = filename.replace("_speech_by_meeting.xlsx", "")
                    if (legislator.hg_nm == name_from_file or 
                        legislator.hg_nm.replace(" ", "") == name_from_file.replace(" ", "")):
                        print(f"  -> 파일 있음: {filename}")
                        found_file = True
                        break
                if not found_file:
                    print(f"  -> 파일 없음")
        
    finally:
        db.close()

from app.models.speech import SpeechByMeeting

if __name__ == "__main__":
    check_file_name_matching()