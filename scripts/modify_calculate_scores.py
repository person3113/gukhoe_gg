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

from app.db.database import SessionLocal

def calculate_participation_scores_all_committees():
    """
    모든 상임위 출석을 고려한 의원별 참여 점수(출석률) 계산하여 DB 업데이트
    
    참여 점수 = (본회의 출석 + 상임위 출석) / (본회의 회의 수 + 상임위 회의 수) × 100
    """
    db = SessionLocal()
    try:
        print("참여 점수(출석률) 계산 시작...")
        
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        print(f"총 {len(legislators)}명의 의원 점수 계산")
        
        updated_count = 0
        for legislator in legislators:
            # 1. 본회의 출석 정보
            plenary_attendance = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "본회의",
                Attendance.status == "출석"
            ).first()
            
            plenary_meetings = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "본회의",
                Attendance.status == "회의일수"
            ).first()
            
            plenary_attendance_count = plenary_attendance.count if plenary_attendance else 0
            plenary_meetings_count = plenary_meetings.count if plenary_meetings else 0
            
            # 2. 상임위 출석 정보 (모든 상임위)
            committee_attendance = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "상임위",
                Attendance.status == "출석"
            ).all()
            
            committee_meetings = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "상임위",
                Attendance.status == "회의일수"
            ).all()
            
            # 상임위 출석 및 회의 수 합산
            committee_attendance_count = sum(a.count for a in committee_attendance)
            committee_meetings_count = sum(m.count for m in committee_meetings)
            
            # 각 상임위 정보 출력
            if committee_attendance:
                committee_info = []
                for att in committee_attendance:
                    committee_name = "알 수 없음"
                    if att.committee_id:
                        committee = db.query(Committee).filter(Committee.id == att.committee_id).first()
                        if committee:
                            committee_name = committee.dept_nm
                    committee_info.append(f"{committee_name}({att.count})")
                
                committee_info_str = ", ".join(committee_info)
            else:
                committee_info_str = "없음"
            
            # 3. 출석 점수 계산
            total_attendance = plenary_attendance_count + committee_attendance_count
            total_meetings = plenary_meetings_count + committee_meetings_count
            
            if total_meetings > 0:
                participation_score = (total_attendance / total_meetings) * 100
                participation_score = round(participation_score, 1)
            else:
                participation_score = 0
            
            # 4. DB 업데이트
            legislator.participation_score = participation_score
            updated_count += 1
            
            # 5. 로그 출력
            print(f"{legislator.hg_nm}: 본회의({plenary_attendance_count}/{plenary_meetings_count}), 상임위({committee_attendance_count}/{committee_meetings_count}) -> 참여 점수: {participation_score}")
            print(f"  상임위 출석: {committee_info_str}")
        
        # 변경사항 저장
        db.commit()
        print(f"참여 점수 계산 완료: {updated_count}명 업데이트")
        
    except Exception as e:
        db.rollback()
        print(f"참여 점수 계산 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    calculate_participation_scores_all_committees()