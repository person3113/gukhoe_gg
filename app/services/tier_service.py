from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.legislator import Legislator

class TierService:
    def __init__(self, db: Session):
        # DB 세션 저장
        self.db = db
        # 티어 정의
        self.tiers = {
            "Challenger": 0.03,  # 상위 0.03%
            "Grandmaster": 0.08,  # 상위 0.08%
            "Master": 0.67,      # 상위 0.67%
            "Diamond": 2.65,     # 상위 2.65%
            "Emerald": 8.76,     # 상위 8.76%
            "Platinum": 11.97,   # 상위 11.97%
            "Gold": 17.81,       # 상위 17.81%
            "Silver": 19.40,     # 상위 19.40%
            "Bronze": 19.85,     # 상위 19.85%
            "Iron": 18.79        # 나머지
        }

    def update_tiers(self) -> None:
        # 호출: db.query(Legislator)로 모든 의원 조회
        # 점수 분포에 따라 티어 할당 (Challenger, Master, Diamond 등)
        # 호출: db.commit()으로 DB에 변경사항 저장
        pass