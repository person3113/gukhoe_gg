import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
from app.models.legislator import Legislator
from app.models.speech import SpeechByMeeting

from app.db.database import SessionLocal


from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def clean_duplicate_speech_data():
    """중복된 발언 데이터 정리"""
    db = SessionLocal()
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        print(f"총 {len(legislators)}명의 의원 데이터 정리 시작")
        
        cleaned_count = 0
        
        for legislator in legislators:
            # 해당 의원의 모든 발언 데이터 조회
            speeches = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id
            ).all()
            
            # 회의 유형별로 그룹화
            speech_dict = {}
            duplicates = []
            
            for speech in speeches:
                key = speech.meeting_type
                if key in speech_dict:
                    # 중복 발견
                    duplicates.append(speech)
                    print(f"중복 발견: {legislator.hg_nm} - {key} (기존: {speech_dict[key].count}, 중복: {speech.count})")
                    
                    # 더 큰 값을 유지
                    if speech.count > speech_dict[key].count:
                        # 기존 것을 삭제 대상으로
                        duplicates.append(speech_dict[key])
                        duplicates.remove(speech)
                        speech_dict[key] = speech
                else:
                    speech_dict[key] = speech
            
            # 중복 제거
            if duplicates:
                print(f"{legislator.hg_nm}: {len(duplicates)}개 중복 제거")
                for dup in duplicates:
                    db.delete(dup)
                cleaned_count += len(duplicates)
        
        # 변경사항 저장
        db.commit()
        print(f"\n총 {cleaned_count}개의 중복 데이터 제거 완료")
        
    except Exception as e:
        db.rollback()
        print(f"중복 데이터 정리 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def verify_cleaned_data():
    """정리된 데이터 검증"""
    db = SessionLocal()
    try:
        print("\n=== 데이터 검증 ===")
        
        # 중복 데이터가 있는지 확인
        from sqlalchemy import func
        
        duplicates = db.query(
            SpeechByMeeting.legislator_id,
            SpeechByMeeting.meeting_type,
            func.count(SpeechByMeeting.id).label('count')
        ).group_by(
            SpeechByMeeting.legislator_id,
            SpeechByMeeting.meeting_type
        ).having(
            func.count(SpeechByMeeting.id) > 1
        ).all()
        
        if duplicates:
            print(f"아직 {len(duplicates)}개의 중복이 남아있습니다:")
            for dup in duplicates[:10]:  # 처음 10개만 표시
                legislator = db.query(Legislator).filter(Legislator.id == dup.legislator_id).first()
                print(f"  - {legislator.hg_nm}: {dup.meeting_type} ({dup.count}개)")
        else:
            print("중복 데이터가 모두 제거되었습니다.")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("중복 발언 데이터 정리를 시작합니다...")
    clean_duplicate_speech_data()
    verify_cleaned_data()