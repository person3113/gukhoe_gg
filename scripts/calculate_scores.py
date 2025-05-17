import sys
import os
from sqlalchemy import func
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.services.tier_service import TierService

# 먼저 모든 모델을 명시적으로 임포트하여 순환 참조 문제 해결
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

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
    pass

def calculate_legislation_scores(db: Session):
    """
    입법활동 점수 계산
    - 대표발의 활동량(60%): 대표발의안 수 / 최대 대표발의안 수 × 100
    - 공동발의 활동량(20%): 공동발의안 수 / 최대 공동발의안 수 × 100
    - 법안 통과 성공률(20%): (원안가결×1.2 + 수정가결×1.0 + 대안반영×0.8) / 대표발의안 수 × 100
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        # 의원별 대표발의안 수, 공동발의안 수, 대표발의 법안 처리 결과 집계
        legislator_scores = []
        max_main_count = 0
        max_co_count = 0
        
        for legislator in legislators:
            # 대표발의안 수 조회
            main_bills_count = db.query(Bill).filter(
                Bill.main_proposer_id == legislator.id
            ).count()
            
            # 공동발의안 수 조회
            co_bills_count = db.query(BillCoProposer).filter(
                BillCoProposer.legislator_id == legislator.id
            ).count()
            
            # 법안 처리 결과 집계
            bills = db.query(Bill).filter(
                Bill.main_proposer_id == legislator.id
            ).all()
            
            # 처리 결과별 합계
            original_pass = 0  # 원안가결
            modified_pass = 0  # 수정가결
            alternative = 0   # 대안반영폐기
            
            for bill in bills:
                if bill.proc_result == "원안가결":
                    original_pass += 1
                elif bill.proc_result == "수정가결":
                    modified_pass += 1
                elif bill.proc_result == "대안반영폐기":
                    alternative += 1
            
            # 의원별 데이터 저장
            legislator_scores.append({
                "id": legislator.id,
                "main_bills_count": main_bills_count,
                "co_bills_count": co_bills_count,
                "original_pass": original_pass,
                "modified_pass": modified_pass,
                "alternative": alternative
            })
            
            # 최대값 갱신
            if main_bills_count > max_main_count:
                max_main_count = main_bills_count
            if co_bills_count > max_co_count:
                max_co_count = co_bills_count
        
        # 최대값이 0인 경우 처리 (0으로 나누기 방지)
        if max_main_count == 0:
            max_main_count = 1
        if max_co_count == 0:
            max_co_count = 1
        
        # 의원별 점수 계산 및 DB 업데이트
        for score_data in legislator_scores:
            legislator_id = score_data["id"]
            
            # 대표발의 활동량 (60%)
            main_activity = (score_data["main_bills_count"] / max_main_count) * 100 * 0.6
            
            # 공동발의 활동량 (20%)
            co_activity = (score_data["co_bills_count"] / max_co_count) * 100 * 0.2
            
            # 법안 통과 성공률 (20%)
            if score_data["main_bills_count"] > 0:
                pass_rate = (
                    (score_data["original_pass"] * 1.2 + 
                     score_data["modified_pass"] * 1.0 + 
                     score_data["alternative"] * 0.8) / 
                    score_data["main_bills_count"] * 100 * 0.2
                )
            else:
                pass_rate = 0
            
            # 총점 계산 (최대 100점)
            total_score = min(main_activity + co_activity + pass_rate, 100)
            
            # DB 업데이트
            legislator = db.query(Legislator).filter(Legislator.id == legislator_id).first()
            if legislator:
                legislator.legislation_score = total_score
        
        # 변경사항 저장
        db.commit()
        print(f"입법활동 점수 계산 완료: {len(legislator_scores)}명")
        
    except Exception as e:
        db.rollback()
        print(f"입법활동 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_speech_scores(db: Session):
    """
    의정발언 점수 계산
    """
    # DB에서 발언 데이터 조회
    # 의원별 발언 횟수, 키워드 다양성 등 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    pass

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
    종합 점수 계산 (모든 스탯에 스케일링 적용)
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        # 전체 스탯의 현재 최대값 찾기
        max_participation = db.query(func.max(Legislator.participation_score)).scalar() or 1
        max_legislation = db.query(func.max(Legislator.legislation_score)).scalar() or 1
        max_speech = db.query(func.max(Legislator.speech_score)).scalar() or 1
        max_voting = db.query(func.max(Legislator.voting_score)).scalar() or 1
        max_cooperation = db.query(func.max(Legislator.cooperation_score)).scalar() or 1
        
        # 스케일링 목표 설정
        TARGET_MAX = 100       # 목표 최대 점수
        TARGET_AVG = 40        # 목표 평균 점수
        BASE_SCORE = 15        # 기본 점수 (최소 15점은 보장)
        
        # 스케일링 계수 계산 (각 스탯을 100점 만점으로 변환)
        scale_participation = (TARGET_MAX - BASE_SCORE) / max_participation if max_participation > 0 else 1
        scale_legislation = (TARGET_MAX - BASE_SCORE) / max_legislation if max_legislation > 0 else 1
        scale_speech = (TARGET_MAX - BASE_SCORE) / max_speech if max_speech > 0 else 1
        scale_voting = (TARGET_MAX - BASE_SCORE) / max_voting if max_voting > 0 else 1
        scale_cooperation = (TARGET_MAX - BASE_SCORE) / max_cooperation if max_cooperation > 0 else 1
        
        print(f"스케일링 계수 - 참여: {scale_participation:.2f}, 입법: {scale_legislation:.2f}, "
              f"발언: {scale_speech:.2f}, 표결: {scale_voting:.2f}, 협치: {scale_cooperation:.2f}")
        
        # 의원별 점수 계산 및 DB 업데이트
        for legislator in legislators:
            # 기존 각 카테고리 점수 (None인 경우 0으로 처리)
            participation = legislator.participation_score or 0
            legislation = legislator.legislation_score or 0
            speech = legislator.speech_score or 0
            voting = legislator.voting_score or 0
            cooperation = legislator.cooperation_score or 0
            
            # 스케일링 적용 (기본 점수 + 스케일링된 점수)
            participation_scaled = min(BASE_SCORE + (participation * scale_participation), 100)
            legislation_scaled = min(BASE_SCORE + (legislation * scale_legislation), 100)
            speech_scaled = min(BASE_SCORE + (speech * scale_speech), 100)
            voting_scaled = min(BASE_SCORE + (voting * scale_voting), 100)
            cooperation_scaled = min(BASE_SCORE + (cooperation * scale_cooperation), 100)
            
            # 스케일링된 점수 저장
            legislator.participation_score = participation_scaled
            legislator.legislation_score = legislation_scaled
            legislator.speech_score = speech_scaled
            legislator.voting_score = voting_scaled
            legislator.cooperation_score = cooperation_scaled
            
            # 가중치에 따른 종합 점수 계산
            overall_score = (
                participation_scaled * 0.15 +  # 참여도 (15%)
                legislation_scaled * 0.4 +     # 입법활동 (40%)
                speech_scaled * 0.25 +         # 의정발언 (25%)
                voting_scaled * 0.1 +          # 표결 책임성 (10%)
                cooperation_scaled * 0.1       # 협치/초당적 활동 (10%)
            )
            
            # 종합 점수 저장
            legislator.overall_score = overall_score
        
        # 변경사항 저장
        db.commit()
        print(f"종합 점수 계산 완료: {len(legislators)}명")
        
    except Exception as e:
        db.rollback()
        print(f"종합 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def update_tiers(db: Session):
    """
    티어 업데이트
    """
    # 호출: TierService(db).update_tiers()로 티어 업데이트
    # DB 업데이트
    pass

def update_rankings(db: Session):
    """
    랭킹 업데이트
    """
    # 호출: update_rankings()로 랭킹 업데이트
    # DB 업데이트
    pass

if __name__ == "__main__":
    calculate_all_scores()