from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.legislator import Legislator
from app.utils.image_path_helper import ImagePathHelper  # 이미지 경로 헬퍼 추가

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/search")
async def search_legislator(request: Request, name: str, db: Session = Depends(get_db)):
    """
    국회의원 이름으로 검색 - 개선된 버전
    
    Args:
        request: FastAPI 요청 객체
        name: 검색할 의원 이름
        db: 데이터베이스 세션
    
    Returns:
        - 결과 1개: 해당 의원 상세페이지로 리다이렉트
        - 결과 여러개: 검색 결과 목록 페이지
        - 결과 0개: 404 페이지
    """
    # 국회의원 이름으로 DB 조회 (부분 일치 검색)
    legislators = db.query(Legislator).filter(
        Legislator.hg_nm.like(f"%{name}%")
    ).order_by(Legislator.hg_nm).all()
    
    # 결과에 따른 분기 처리
    if len(legislators) == 1:
        # 결과가 1개인 경우: 바로 해당 의원 상세페이지로 리다이렉트
        return RedirectResponse(f"/champions/{legislators[0].id}", status_code=302)
    elif len(legislators) > 1:
        # 결과가 여러개인 경우: 검색 결과 목록 페이지 표시
        # ORM 객체를 딕셔너리로 변환
        search_results = []
        for legislator in legislators:
            # 이미지 URL을 최적화된 리스트 이미지로 변경 (80x80 대신 list 이미지 사용)
            profile_image_url = legislator.profile_image_url
            if profile_image_url:
                # 파일명만 추출
                filename = profile_image_url.split('/')[-1]
                profile_image_url = ImagePathHelper.get_optimized_image_path(filename, "list")
            else:
                profile_image_url = "/static/images/legislators/default.png"
                
            search_results.append({
                "id": legislator.id,
                "name": legislator.hg_nm,
                "party": legislator.poly_nm,
                "district": legislator.orig_nm,
                "term": legislator.reele_gbn_nm,
                "tier": legislator.tier,
                "profile_image_url": profile_image_url
            })
        
        return templates.TemplateResponse(
            "search_results.html", 
            {
                "request": request,
                "search_results": search_results,
                "search_term": name,
                "result_count": len(search_results)
            }
        )
    else:
        # 결과가 없는 경우: 404 페이지
        return templates.TemplateResponse(
            "404.html", 
            {
                "request": request, 
                "message": f"'{name}'이 포함된 국회의원을 찾을 수 없습니다."
            }
        )

def redirect_to_legislator_detail(legislator_id: int):
    """의원 상세 페이지로 리다이렉트하는 헬퍼 함수"""
    return RedirectResponse(f"/champions/{legislator_id}", status_code=302)