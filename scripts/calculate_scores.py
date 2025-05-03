import sys
import os
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    pass

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