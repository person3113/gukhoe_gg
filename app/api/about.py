from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/about")
async def about(request: Request):
    """
    국회.gg 소개 페이지
    
    Args:
        request: FastAPI 요청 객체
    
    Returns:
        템플릿 렌더링 응답
    """
    return templates.TemplateResponse("about.html", {"request": request})