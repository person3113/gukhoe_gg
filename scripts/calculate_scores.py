import sys
import os
from sqlalchemy.orm import Session

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
from app.services.ranking_service import RankingService
from app.services.tier_service import TierService

def calculate_all_scores():
    """
    모든 점수 계산 함수 호출
    """
    # DB 세션 생성
    db = SessionLocal()
    try:
        print("Calculating all scores...")
        calculate_participation_scores(db)
        calculate_legislation_scores(db)
        calculate_speech_scores(db)
        calculate_voting_scores(db)
        calculate_cooperation_scores(db)
        calculate_overall_scores(db)
        update_tiers(db)
        update_rankings(db)
        print("Score calculation completed.")
    finally:
        db.close()

def calculate_participation_scores(db: Session):
    """
    참여 점수 계산
    """
    # DB에서 출석 데이터 조회
    # 의원별 출석률 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    """
    의원별 참여 점수(출석률) 계산하여 DB 업데이트
    
    참여 점수 = (의원이 출석한 회의 수 / 의원이 참석해야 할 회의 수) × 100
    * 참석해야 할 회의: 본회의 + 소속 위원회의 회의
    
    Args:
        db: 데이터베이스 세션
    """
    from app.models.attendance import Attendance
    from app.models.legislator import Legislator
    from app.models.committee import Committee, CommitteeMember
    from sqlalchemy import func, distinct, and_, or_
    
    try:
        print("참여 점수(출석률) 계산 시작...")
        
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        print(f"총 {len(legislators)}명의 의원 점수 계산")
        
        # 전체 본회의 날짜 목록 (모든 의원이 참석해야 함)
        plenary_meeting_dates = db.query(distinct(Attendance.meeting_date)).filter(
            Attendance.meeting_type == "본회의"
        ).all()
        plenary_meeting_dates = [date[0] for date in plenary_meeting_dates]
        
        # 의원별 출석 점수 계산
        updated_count = 0
        for legislator in legislators:
            # 1. 해당 의원의 소속 위원회 ID 목록
            committee_ids = db.query(CommitteeMember.committee_id).filter(
                CommitteeMember.legislator_id == legislator.id
            ).all()
            committee_ids = [id[0] for id in committee_ids]
            
            # 2. 의원이 참석해야 할 회의 수 계산
            # 2-1. 본회의는 모든 의원이 참석해야 함
            required_plenary_count = len(plenary_meeting_dates)
            
            # 2-2. 소속 위원회의 회의
            required_committee_meetings = []
            if committee_ids:
                committee_meetings = db.query(distinct(Attendance.meeting_date, Attendance.committee_id)).filter(
                    Attendance.meeting_type == "상임위",
                    Attendance.committee_id.in_(committee_ids)
                ).all()
                required_committee_meetings = committee_meetings
            
            required_committee_count = len(required_committee_meetings)
            required_total_count = required_plenary_count + required_committee_count
            
            # 3. 의원의 출석 횟수 계산
            # 3-1. 본회의 출석
            plenary_attendance = db.query(func.count()).filter(
                Attendance.legislator_id == legislator.id,
                Attendance.meeting_type == "본회의",
                Attendance.status == "출석"
            ).scalar() or 0
            
            # 3-2. 상임위 출석 (소속 위원회만)
            committee_attendance = 0
            if committee_ids:
                committee_attendance = db.query(func.count()).filter(
                    Attendance.legislator_id == legislator.id,
                    Attendance.meeting_type == "상임위",
                    Attendance.committee_id.in_(committee_ids),
                    Attendance.status == "출석"
                ).scalar() or 0
            
            total_attendance = plenary_attendance + committee_attendance
            
            # 4. 참여 점수 계산 (0~100)
            if required_total_count > 0:
                participation_score = (total_attendance / required_total_count) * 100
                participation_score = round(participation_score, 1)  # 소수점 첫째 자리까지
            else:
                participation_score = 0
            
            # 5. DB 업데이트
            legislator.participation_score = participation_score
            updated_count += 1
            
            # 6. 로그 출력
            committee_names = ""
            if committee_ids:
                committee_query = db.query(Committee.dept_nm).filter(Committee.id.in_(committee_ids)).all()
                committee_names = ", ".join([c[0] for c in committee_query])
            
            print(f"{legislator.hg_nm}: 본회의({plenary_attendance}/{required_plenary_count}), 상임위({committee_attendance}/{required_committee_count}) -> 참여 점수: {participation_score}")
            if committee_names:
                print(f"  소속 위원회: {committee_names}")
        
        # 변경사항 저장
        db.commit()
        print(f"참여 점수 계산 완료: {updated_count}명 업데이트")
        
    except Exception as e:
        db.rollback()
        print(f"참여 점수 계산 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_legislation_scores(db: Session):
    """
    입법활동 점수 계산
    """
    # DB에서 법안 데이터 조회
    # 의원별 대표발의안수, 공동발의안수 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    pass

def calculate_speech_scores(db: Session):
    """
    의정발언 점수 계산
    """
    # DB에서 발언 데이터 조회
    # 의원별 발언 횟수, 키워드 다양성 등 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    """
    의정발언 점수 계산 - Total 값을 그대로 speech_score에 저장
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        print(f"총 {len(legislators)}명의 의원 점수 계산 시작")
        
        # 각 의원의 Total 발언수를 그대로 speech_score에 저장
        updated_count = 0
        for legislator in legislators:
            try:
                # Total 발언수 조회
                total_speech = db.query(SpeechByMeeting).filter(
                    SpeechByMeeting.legislator_id == legislator.id,
                    SpeechByMeeting.meeting_type == "Total"
                ).first()
                
                if total_speech and total_speech.count is not None:
                    # Total 값을 그대로 speech_score에 저장
                    try:
                        legislator.speech_score = float(total_speech.count)
                        updated_count += 1
                        print(f"{legislator.hg_nm}: Total={total_speech.count} -> speech_score={legislator.speech_score}")
                    except (ValueError, TypeError) as e:
                        print(f"경고: {legislator.hg_nm}의 발언 수({total_speech.count})를 float로 변환할 수 없습니다: {e}")
                        legislator.speech_score = 0.0
                else:
                    # Total 값이 없으면 0으로 설정
                    legislator.speech_score = 0.0
                    print(f"{legislator.hg_nm}: Total 없음 -> speech_score=0")
            except Exception as e:
                # 의원별 처리 중 오류 발생 시 해당 의원만 스킵하고 계속 진행
                print(f"의원 {legislator.hg_nm} 처리 중 오류 발생: {str(e)}")
                continue
        
        # 변경사항 저장
        db.commit()
        print(f"의정발언 점수 계산 완료: {updated_count}명 업데이트")
        
    except Exception as e:
        db.rollback()
        print(f"의정발언 점수 계산 오류: {str(e)}")
        import traceback
        traceback.print_exc()


def calculate_voting_scores(db: Session):
    """
    표결 책임성 점수 계산
    """
    # DB에서 표결 데이터 조회
    # 의원별 기권률, 불참률 계산
    # 점수 산출 알고리즘 적용 (낮을수록 높은 점수)
    # DB 업데이트
    pass

def calculate_cooperation_scores(db: Session):
    """
    협치/초당적 활동 점수 계산
    """
    # DB에서 법안 공동발의 데이터 조회
    # 의원별 타 정당 의원과 공동발의 비율 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    pass

def calculate_overall_scores(db: Session):
    """
    종합 점수 계산
    """
    # 각 카테고리별 점수에 가중치 적용
    # 의원별 종합 점수 계산
    # DB 업데이트
    pass

def update_tiers(db: Session):
    """
    티어 업데이트
    """
    # 호출: TierService(db).update_tiers()로 티어 업데이트
    # DB 업데이트
    tier_service = TierService(db)
    tier_service.update_tiers()
    pass

def update_rankings(db: Session):
    """
    랭킹 업데이트
    """
    # 호출: RankingService(db).update_rankings()로 랭킹 업데이트
    # DB 업데이트
    ranking_service = RankingService(db)
    ranking_service.update_rankings()
    pass

if __name__ == "__main__":
    calculate_all_scores()
   