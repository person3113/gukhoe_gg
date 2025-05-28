from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response
from typing import Optional
import os

from app.utils.image_optimizer import ImageOptimizer

router = APIRouter()
image_optimizer = ImageOptimizer()

@router.get("/images/legislators/{file_name}")
async def get_legislator_image(
    request: Request,
    file_name: str,
    width: Optional[int] = None,
    height: Optional[int] = None
):
    """
    의원 이미지 최적화 엔드포인트
    
    Args:
        request: FastAPI 요청 객체
        file_name: 이미지 파일명
        width: 변경할 너비
        height: 변경할 높이
    
    Returns:
        최적화된 이미지 응답
    """
    # 이미지 경로 생성
    image_path = os.path.join("app/static/images/legislators", file_name)
    
    # 이미지 최적화 및 응답
    return await image_optimizer.optimize_image_response(request, image_path, width, height) 