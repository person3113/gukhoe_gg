from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.legislator import Legislator

router = APIRouter()

@router.get("/search")
async def search_legislator(name: str, db: Session = Depends(get_db)):
    # 호출: db.query(Legislator)로 이름으로 의원 검색
    # 의원 발견 시 redirect_to_legislator_detail() 호출
    # 의원 미발견 시 오류 메시지 반환
    pass

def redirect_to_legislator_detail(legislator_id: int):
    # 호출: RedirectResponse()로 의원 상세 페이지 URL 생성
    # 반환: 리다이렉트 응답
    pass