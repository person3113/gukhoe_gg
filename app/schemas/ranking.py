from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class RankingFilter(BaseModel):
    # 랭킹 필터링 조건
    category: str = "overall"  # overall, participation, legislation, speech, voting, cooperation
    party: Optional[str] = None
    committee: Optional[str] = None
    term: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    asset_group: Optional[str] = None

class RankingResult(BaseModel):
    # 랭킹 결과
    id: int
    rank: int
    name: str
    party: str
    tier: str
    score: float
    
    class Config:
        orm_mode = True

class CategoryRanking(BaseModel):
    # 카테고리별 랭킹 정보
    top: List[RankingResult]
    bottom: List[RankingResult]
    all: List[RankingResult]
    chart_data: Dict[str, Any]

class StatsSummary(BaseModel):
    # 통계 요약 정보
    avg: float
    max: float
    min: float
    tier_distribution: Dict[str, int]
    party_distribution: Optional[Dict[str, int]] = None
    term_distribution: Optional[Dict[str, int]] = None
    age_distribution: Optional[Dict[str, int]] = None

class ChartData(BaseModel):
    # 차트 데이터
    labels: List[str]
    datasets: List[Dict[str, Any]]