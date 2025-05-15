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

# DB 관련 import
from app.db.database import SessionLocal
from sqlalchemy import func

def check_attendance_data():
    """DB에 저장된 출석 데이터 확인"""
    db = SessionLocal()
    try:
        # 전체 통계
        total_attendance = db.query(Attendance).count()
        
        print("\n=== 출석 데이터 전체 통계 ===")
        print(f"총 출석 데이터 수: {total_attendance}개")
        
        # count > 0인 데이터 수 (요약 데이터)
        summary_data_count = db.query(Attendance).filter(Attendance.count > 0).count()
        print(f"요약 데이터 수: {summary_data_count}개")
        
        # 회의 유형별 통계
        meeting_types = db.query(
            Attendance.meeting_type, 
            func.count().label('count')
        ).group_by(Attendance.meeting_type).all()
        
        print("\n=== 회의 유형별 통계 ===")
        for meeting_type, count in meeting_types:
            print(f"{meeting_type}: {count}개")
        
        # 출석 상태별 통계
        status_counts = db.query(
            Attendance.status, 
            func.count().label('count')
        ).group_by(Attendance.status).all()
        
        print("\n=== 출석 상태별 통계 ===")
        for status, count in status_counts:
            print(f"{status}: {count}개")
        
        # 의원별 출석 데이터 샘플
        print("\n=== 의원별 출석 데이터 샘플 (상위 5명) ===")
        
        legislators = db.query(Legislator).limit(5).all()
        for i, legislator in enumerate(legislators, 1):
            print(f"\n{i}. {legislator.hg_nm} ({legislator.poly_nm})")
            
            # 본회의 데이터
            plenary_data = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "본회의"
            ).all()
            
            if plenary_data:
                print("  본회의:")
                for attendance in plenary_data:
                    print(f"    - {attendance.status}: {attendance.count}")
            
            # 상임위 데이터
            committee_data = db.query(Attendance).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "상임위"
            ).all()
            
            if committee_data:
                print("  상임위:")
                for attendance in committee_data:
                    committee_name = ""
                    if attendance.committee_id:
                        committee = db.query(Committee).filter(
                            Committee.id == attendance.committee_id
                        ).first()
                        if committee:
                            committee_name = f" ({committee.dept_nm})"
                    print(f"    - {attendance.status}{committee_name}: {attendance.count}")
            
            # 참여 점수 확인
            if legislator.participation_score is not None:
                print(f"  참여 점수: {legislator.participation_score}")
        
        # 참여 점수 통계
        score_count = db.query(Legislator).filter(
            Legislator.participation_score != None,
            Legislator.participation_score > 0
        ).count()
        
        print(f"\n=== 참여 점수 ===")
        print(f"참여 점수가 계산된 의원 수: {score_count}명")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_attendance_data()