from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.legislator import Legislator

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/search")
async def search_legislator(request: Request, name: str, db: Session = Depends(get_db)):
    """
    국회의원 이름으로 검색해서 해당 의원 페이지로 리다이렉트
    
    Args:
        request: FastAPI 요청 객체
        name: 검색할 의원 이름
        db: 데이터베이스 세션
    
    Returns:
        RedirectResponse 또는 404 템플릿
    """
    # 국회의원 이름으로 DB 조회 (부분 일치 검색)
    legislator = db.query(Legislator).filter(Legislator.hg_nm.like(f"%{name}%")).first()
    
    # 의원 정보가 있으면 상세 페이지로 리다이렉트
    if legislator:
        return redirect_to_legislator_detail(legislator.id)
    
    # 의원 정보가 없으면 404 템플릿 렌더링
    return templates.TemplateResponse(
        "404.html", 
        {"request": request, "message": f"'{name}'(이)라는 이름의 국회의원을 찾을 수 없습니다."}
    )

def redirect_to_legislator_detail(legislator_id: int):
    """
    국회의원 상세 페이지로 리다이렉트
    
    Args:
        legislator_id: 국회의원 ID
    
    Returns:
        RedirectResponse: 의원 상세 페이지로 리다이렉트
    """
    # 국회의원 상세 페이지 URL 생성 및 리다이렉트
    redirect_url = f"/champions/{legislator_id}"
    return RedirectResponse(url=redirect_url)