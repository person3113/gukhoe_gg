import os
from typing import Optional

class ImagePathHelper:
    """
    화면별 최적화된 이미지 경로를 제공하는 유틸리티 클래스
    """
    
    BASE_PATH = "/static/images/legislators"
    OPTIMIZED_BASE_PATH = "/static/images/legislators_optimized"
    DEFAULT_IMAGE = f"{BASE_PATH}/default.png"
    
    @classmethod
    def get_detail_image_path(cls, filename: str) -> str:
        """
        상세 페이지용 이미지 경로 (400px 너비)
        
        Args:
            filename: 이미지 파일명
            
        Returns:
            최적화된 이미지 경로
        """
        # 외부 URL이거나 파일명이 없는 경우 기본 이미지 반환
        if not filename or filename.startswith('http'):
            return cls.DEFAULT_IMAGE
            
        # 최적화된 이미지 경로
        optimized_path = f"{cls.OPTIMIZED_BASE_PATH}/detail/{filename}"
        
        # 최적화된 이미지가 없으면 원본 사용
        if not os.path.exists(f"app{optimized_path}"):
            return f"{cls.BASE_PATH}/{filename}"
            
        return optimized_path
    
    @classmethod
    def get_list_image_path(cls, filename: str) -> str:
        """
        목록 페이지용 이미지 경로 (200x200)
        
        Args:
            filename: 이미지 파일명
            
        Returns:
            최적화된 이미지 경로
        """
        # 외부 URL이거나 파일명이 없는 경우 기본 이미지 반환
        if not filename or filename.startswith('http'):
            return cls.DEFAULT_IMAGE
            
        # 최적화된 이미지 경로
        optimized_path = f"{cls.OPTIMIZED_BASE_PATH}/list/{filename}"
        
        # 최적화된 이미지가 없으면 원본 사용
        if not os.path.exists(f"app{optimized_path}"):
            return f"{cls.BASE_PATH}/{filename}"
            
        return optimized_path
    
    @classmethod
    def get_thumb_image_path(cls, filename: str) -> str:
        """
        썸네일용 이미지 경로 (40x40)
        
        Args:
            filename: 이미지 파일명
            
        Returns:
            최적화된 이미지 경로
        """
        # 외부 URL이거나 파일명이 없는 경우 기본 이미지 반환
        if not filename or filename.startswith('http'):
            return cls.DEFAULT_IMAGE
            
        # 최적화된 이미지 경로
        optimized_path = f"{cls.OPTIMIZED_BASE_PATH}/thumb/{filename}"
        
        # 최적화된 이미지가 없으면 원본 사용
        if not os.path.exists(f"app{optimized_path}"):
            return f"{cls.BASE_PATH}/{filename}"
            
        return optimized_path
    
    @classmethod
    def get_optimized_image_path(cls, filename: str, image_type: str = "list") -> str:
        """
        용도에 맞는 최적화된 이미지 경로
        
        Args:
            filename: 이미지 파일명
            image_type: 이미지 유형 (detail, list, thumb)
            
        Returns:
            최적화된 이미지 경로
        """
        if image_type == "detail":
            return cls.get_detail_image_path(filename)
        elif image_type == "thumb":
            return cls.get_thumb_image_path(filename)
        else:  # 기본값은 list
            return cls.get_list_image_path(filename) 