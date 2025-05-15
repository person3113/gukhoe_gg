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
from sqlalchemy import func, distinct, and_, or_

def check_attendance_data():
    """DB에 저장된 출석 데이터 확인"""
    db = SessionLocal()
    try:
        # 전체 통계
        total_attendance = db.query(Attendance).count()
        
        # distinct를 사용할 때는 단일 컬럼만 가능하므로 다른 방식으로 수정
        distinct_meetings = db.query(Attendance.meeting_date, Attendance.meeting_type).distinct().count()
        distinct_legislators = db.query(Attendance.legislator_id).distinct().count()
        
        print("\n=== 출석 데이터 전체 통계 ===")
        print(f"총 출석 데이터 수: {total_attendance}개")
        print(f"고유 회의 수: {distinct_meetings}개")
        print(f"출석 데이터가 있는 의원 수: {distinct_legislators}명")
        
        # 회의 유형별 통계
        meeting_types = db.query(Attendance.meeting_type, func.count().label('count')).group_by(Attendance.meeting_type).all()
        print("\n=== 회의 유형별 통계 ===")
        for meeting_type, count in meeting_types:
            print(f"{meeting_type}: {count}개")
        
        # 출석 상태별 통계
        status_counts = db.query(Attendance.status, func.count().label('count')).group_by(Attendance.status).all()
        print("\n=== 출석 상태별 통계 ===")
        for status, count in status_counts:
            print(f"{status}: {count}개")
            
        # 전체 의원 목록 (출석 데이터가 있는 의원만)
        legislators_with_attendance = db.query(
            Legislator.id, Legislator.hg_nm, Legislator.poly_nm
        ).join(
            Attendance, Legislator.id == Attendance.legislator_id
        ).distinct().all()
        
        print(f"\n=== 의원별 출석률 (총 {len(legislators_with_attendance)}명) ===")
        
        # 각 의원별 출석 통계
        for i, (legislator_id, name, party) in enumerate(legislators_with_attendance, 1):
            # 해당 의원의 소속 위원회 ID 목록
            committee_ids = db.query(CommitteeMember.committee_id).filter(
                CommitteeMember.legislator_id == legislator_id
            ).all()
            committee_ids = [id[0] for id in committee_ids]
            
            # 소속 위원회 이름 목록
            committee_names = ""
            if committee_ids:
                committees = db.query(Committee.dept_nm).filter(
                    Committee.id.in_(committee_ids)
                ).all()
                committee_names = ", ".join([c[0] for c in committees])
            
            # 본회의 참여 횟수
            # 1. 전체 본회의 수
            total_plenary_meetings = db.query(
                Attendance.meeting_date
            ).filter(
                Attendance.meeting_type == "본회의"
            ).distinct().count()
            
            # 2. 해당 의원의 본회의 출석 수
            plenary_attendance = db.query(func.count()).filter(
                Attendance.legislator_id == legislator_id,
                Attendance.meeting_type == "본회의",
                Attendance.status == "출석"
            ).scalar() or 0
            
            # 상임위 참여 횟수
            # 1. 소속 위원회의 회의 수
            total_committee_meetings = 0
            if committee_ids:
                # 여러 컬럼 distinct 수정
                total_committee_meetings = db.query(
                    Attendance.meeting_date, Attendance.committee_id
                ).filter(
                    Attendance.meeting_type == "상임위",
                    Attendance.committee_id.in_(committee_ids)
                ).distinct().count()
            
            # 2. 해당 의원의 상임위 출석 수
            committee_attendance = 0
            if committee_ids:
                committee_attendance = db.query(func.count()).filter(
                    Attendance.legislator_id == legislator_id,
                    Attendance.meeting_type == "상임위",
                    Attendance.committee_id.in_(committee_ids),
                    Attendance.status == "출석"
                ).scalar() or 0
            
            # 전체 통계
            total_meetings = total_plenary_meetings + total_committee_meetings
            total_attendance_count = plenary_attendance + committee_attendance
            
            # 출석률 계산
            attendance_rate = 0
            if total_meetings > 0:
                attendance_rate = (total_attendance_count / total_meetings) * 100
            
            # 의원 정보 출력
            print(f"\n{i}. {name} ({party})")
            if committee_names:
                print(f"   소속 위원회: {committee_names}")
            
            try:
                plenary_rate = (plenary_attendance/total_plenary_meetings*100) if total_plenary_meetings > 0 else 0
                print(f"   본회의: {plenary_attendance}/{total_plenary_meetings} ({plenary_rate:.1f}% 출석)")
            except ZeroDivisionError:
                print("   본회의: 데이터 없음")
                
            try:
                committee_rate = (committee_attendance/total_committee_meetings*100) if total_committee_meetings > 0 else 0
                print(f"   상임위: {committee_attendance}/{total_committee_meetings} ({committee_rate:.1f}% 출석)")
            except ZeroDivisionError:
                print("   상임위: 데이터 없음")
                
            print(f"   총계: {total_attendance_count}/{total_meetings} ({attendance_rate:.1f}% 출석)")
            
            # DB에 저장된 참여 점수 조회
            legislator = db.query(Legislator).filter(Legislator.id == legislator_id).first()
            if legislator and legislator.participation_score is not None:
                print(f"   참여 점수(DB): {legislator.participation_score:.1f}")
                
                # 계산된 출석률과 DB의 참여 점수 비교
                diff = abs(attendance_rate - legislator.participation_score)
                if diff > 0.1:  # 0.1% 이상 차이나면 경고 출력
                    print(f"   [경고] 계산된 출석률({attendance_rate:.1f}%)과 DB의 참여 점수({legislator.participation_score:.1f}%)가 다릅니다.")
        
        # 특정 의원 상세 정보 조회 (선택 사항)
        print("\n=== 특정 의원 상세 조회 ===")
        legislator_name = input("조회할 의원 이름을 입력하세요 (없으면 Enter): ")
        if legislator_name:
            legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
            if legislator:
                print(f"\n{legislator.hg_nm} 의원 출석 정보:")
                print(f"참여 점수: {legislator.participation_score:.1f}")
                
                # 회의 출석 목록
                attendances = db.query(Attendance).filter(
                    Attendance.legislator_id == legislator.id
                ).order_by(Attendance.meeting_date, Attendance.meeting_type).all()
                
                if attendances:
                    print("\n출석 기록:")
                    for i, attendance in enumerate(attendances[:20], 1):  # 최대 20개만 표시
                        committee_name = ""
                        if attendance.committee_id:
                            committee = db.query(Committee).filter(Committee.id == attendance.committee_id).first()
                            if committee:
                                committee_name = f" ({committee.dept_nm})"
                        
                        print(f"{i}. {attendance.meeting_date} - {attendance.meeting_type}{committee_name}: {attendance.status}")
                    
                    if len(attendances) > 20:
                        print(f"... 외 {len(attendances) - 20}개 더 있음")
                else:
                    print("출석 기록이 없습니다.")
            else:
                print(f"{legislator_name} 의원을 찾을 수 없습니다.")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_attendance_data()