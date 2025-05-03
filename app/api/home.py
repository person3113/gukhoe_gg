from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import ranking_service, chart_service

router = APIRouter()

@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # 호출: ranking_service.get_top_legislators()로 상위 의원 조회
    # 호출: chart_service.generate_top_score_chart_data()로 차트 데이터 생성
    # 반환: 템플릿 렌더링(home.html)
    pass