# scripts/debug_attendance_committee.py
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

def debug_attendance_committee():
    """출석 데이터와 위원회 멤버십 확인"""
    db = SessionLocal()
    try:
        # 1. 전체 위원회 목록 확인
        committees = db.query(Committee).all()
        print("=== 전체 위원회 목록 ===")
        for comm in committees[:5]:
            print(f"{comm.id}. {comm.dept_nm}")
        print(f"총 {len(committees)}개 위원회\n")
        
        # 2. 특정 의원의 위원회 멤버십 확인
        print("=== 의원별 위원회 멤버십 및 상임위 출석 데이터 ===")
        legislators = db.query(Legislator).limit(10).all()
        
        for legislator in legislators:
            print(f"\n{legislator.hg_nm} ({legislator.poly_nm})")
            
            # 소속 위원회 확인
            memberships = db.query(CommitteeMember).filter(
                CommitteeMember.legislator_id == legislator.id
            ).all()
            
            if memberships:
                print("  소속 위원회:")
                for mem in memberships:
                    committee = db.query(Committee).filter(Committee.id == mem.committee_id).first()
                    if committee:
                        print(f"    - {committee.dept_nm} (ID: {committee.id})")
            else:
                print("  소속 위원회: 없음")
            
            # 상임위 출석 데이터 확인
            attendance_data = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "상임위"
            ).all()
            
            if attendance_data:
                print("  상임위 출석 데이터:")
                for att in attendance_data:
                    committee_name = "알 수 없음"
                    if att.committee_id:
                        committee = db.query(Committee).filter(Committee.id == att.committee_id).first()
                        if committee:
                            committee_name = committee.dept_nm
                    print(f"    - {committee_name} (ID: {att.committee_id}): {att.status} - {att.count}")
            else:
                print("  상임위 출석 데이터: 없음")
        
        # 3. 상임위 출석 데이터 통계
        print("\n=== 상임위 출석 데이터 통계 ===")
        committee_attendance_count = db.query(Attendance).filter(
            Attendance.meeting_type == "상임위"
        ).count()
        
        committee_attendance_with_id = db.query(Attendance).filter(
            Attendance.meeting_type == "상임위",
            Attendance.committee_id != None
        ).count()
        
        print(f"총 상임위 출석 데이터: {committee_attendance_count}개")
        print(f"위원회 ID가 있는 데이터: {committee_attendance_with_id}개")
        print(f"위원회 ID가 없는 데이터: {committee_attendance_count - committee_attendance_with_id}개")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_attendance_committee()