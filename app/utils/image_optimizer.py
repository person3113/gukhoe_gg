import os
import io
import hashlib
from PIL import Image
from fastapi import Request
from fastapi.responses import Response, StreamingResponse
from typing import Optional, Tuple
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageOptimizer:
    """이미지 최적화를 위한 클래스"""
    
    def __init__(self, cache_dir: str = "app/static/cache"):
        """
        이미지 최적화 클래스 초기화
        
        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"이미지 캐시 디렉토리 설정: {cache_dir}")
    
    def optimize_image(self, image_path: str, width: Optional[int] = None, 
                      height: Optional[int] = None, quality: int = 85) -> Tuple[bytes, str]:
        """
        이미지 최적화 및 리사이징
        
        Args:
            image_path: 이미지 파일 경로
            width: 변경할 너비 (None이면 원본 유지)
            height: 변경할 높이 (None이면 원본 유지)
            quality: JPEG 압축 품질 (1-100)
            
        Returns:
            최적화된 이미지 바이트와 MIME 타입
        """
        # 캐시 키 생성
        cache_key = self._generate_cache_key(image_path, width, height, quality)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        # 캐시 확인
        if os.path.exists(cache_path):
            logger.info(f"캐시된 이미지 사용: {cache_path}")
            with open(cache_path, 'rb') as f:
                return f.read(), self._get_mime_type(image_path)
        
        try:
            # 이미지 파일이 없으면 로깅
            if not os.path.exists(image_path):
                logger.warning(f"이미지 파일을 찾을 수 없음: {image_path}")
                return None, None
            
            # 이미지 열기
            img = Image.open(image_path)
            
            # 리사이징
            if width and height:
                img = img.resize((width, height), Image.LANCZOS)
            elif width:
                ratio = width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((width, new_height), Image.LANCZOS)
            elif height:
                ratio = height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, height), Image.LANCZOS)
            
            # 이미지 포맷 결정
            img_format = 'JPEG'
            mime_type = 'image/jpeg'
            if image_path.lower().endswith('.png'):
                img_format = 'PNG'
                mime_type = 'image/png'
            elif image_path.lower().endswith('.webp'):
                img_format = 'WEBP'
                mime_type = 'image/webp'
            
            # 이미지를 바이트로 변환
            img_byte_arr = io.BytesIO()
            if img_format == 'JPEG':
                img = img.convert('RGB')  # JPEG는 알파 채널 지원 안함
                img.save(img_byte_arr, format=img_format, quality=quality, optimize=True)
            else:
                img.save(img_byte_arr, format=img_format, optimize=True)
            
            img_bytes = img_byte_arr.getvalue()
            
            # 캐시에 저장
            with open(cache_path, 'wb') as f:
                f.write(img_bytes)
            
            logger.info(f"이미지 최적화 완료: {image_path} -> {cache_path}")
            
            return img_bytes, mime_type
        
        except Exception as e:
            logger.error(f"이미지 최적화 중 오류 발생: {e}")
            return None, None
    
    def _generate_cache_key(self, image_path: str, width: Optional[int], 
                           height: Optional[int], quality: int) -> str:
        """캐시 키 생성"""
        file_name = os.path.basename(image_path)
        name, ext = os.path.splitext(file_name)
        
        # 크기가 지정되지 않은 경우 원본 크기로 표시
        width_str = str(width) if width else 'orig'
        height_str = str(height) if height else 'orig'
        
        # 캐시 키 생성
        key = f"{name}_{width_str}x{height_str}_{quality}{ext}"
        
        # 파일명이 너무 길면 해시 처리
        if len(key) > 100:
            hash_obj = hashlib.md5(key.encode())
            key = f"{hash_obj.hexdigest()}_{width_str}x{height_str}_{quality}{ext}"
        
        return key
    
    def _get_mime_type(self, image_path: str) -> str:
        """파일 확장자에 따른 MIME 타입 반환"""
        if image_path.lower().endswith('.png'):
            return 'image/png'
        elif image_path.lower().endswith('.webp'):
            return 'image/webp'
        else:
            return 'image/jpeg'  # 기본값은 JPEG
            
    async def optimize_image_response(self, request: Request, image_path: str, 
                                     width: Optional[int] = None, 
                                     height: Optional[int] = None) -> Response:
        """
        이미지를 최적화하여 응답으로 반환
        
        Args:
            request: FastAPI 요청 객체
            image_path: 이미지 파일 경로
            width: 변경할 너비
            height: 변경할 높이
            
        Returns:
            최적화된 이미지 응답
        """
        # 이미지가 존재하는지 확인
        if not os.path.exists(image_path):
            logger.warning(f"이미지 파일을 찾을 수 없음: {image_path}")
            return Response(status_code=404)
        
        # 요청 헤더에서 캐시 관련 정보 확인
        if_none_match = request.headers.get('if-none-match')
        
        # 이미지 정보 가져오기
        image_stat = os.stat(image_path)
        etag = f'"{image_stat.st_mtime}"'
        
        # 304 Not Modified 응답
        if if_none_match == etag:
            return Response(status_code=304)
        
        # 이미지 최적화
        image_bytes, mime_type = self.optimize_image(image_path, width, height)
        if not image_bytes:
            return Response(status_code=500)
        
        # 응답 헤더 설정
        headers = {
            'Cache-Control': 'public, max-age=31536000',  # 1년
            'ETag': etag
        }
        
        # 최적화된 이미지 응답
        return StreamingResponse(
            io.BytesIO(image_bytes), 
            media_type=mime_type, 
            headers=headers
        ) 