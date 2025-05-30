import os
import sys
from PIL import Image
import logging
import shutil

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_images(input_dir, output_dir, max_width=800, quality=85):
    """
    이미지 최적화 함수
    
    Args:
        input_dir: 입력 이미지 디렉토리
        output_dir: 출력 이미지 디렉토리
        max_width: 최대 너비 (높이는 비율에 맞게 자동 조정)
        quality: JPEG 압축 품질 (1-100)
    """
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"출력 디렉토리 생성: {output_dir}")
    
    # 입력 디렉토리의 모든 파일 처리
    total_files = 0
    processed_files = 0
    total_size_before = 0
    total_size_after = 0
    
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        # 파일이 아니면 무시
        if not os.path.isfile(file_path):
            continue
        
        # 이미지 파일 확장자 확인
        _, ext = os.path.splitext(filename)
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
            continue
        
        # 이미지 파일 처리
        try:
            total_files += 1
            output_path = os.path.join(output_dir, filename)
            
            # 이미지 크기 체크
            file_size_before = os.path.getsize(file_path) / 1024  # KB
            total_size_before += file_size_before
            
            # 이미지 열기
            img = Image.open(file_path)
            
            # 원본 크기 저장
            width, height = img.size
            
            # 이미지 크기 조정 (너비가 max_width보다 크면)
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
                logger.info(f"이미지 크기 조정: {filename}, {width}x{height} -> {max_width}x{new_height}")
            
            # 이미지 포맷 결정
            img_format = 'JPEG'
            if ext.lower() == '.png':
                img_format = 'PNG'
            elif ext.lower() == '.webp':
                img_format = 'WEBP'
            
            # 이미지 저장
            if img_format == 'JPEG':
                img = img.convert('RGB')  # JPEG는 알파 채널 지원 안함
                img.save(output_path, format=img_format, quality=quality, optimize=True)
            else:
                img.save(output_path, format=img_format, optimize=True)
            
            # 최적화 후 크기 체크
            file_size_after = os.path.getsize(output_path) / 1024
            total_size_after += file_size_after
            
            # 결과 기록
            size_reduction = 100 - (file_size_after / file_size_before * 100) if file_size_before > 0 else 0
            logger.info(f"최적화 완료: {filename}, {file_size_before:.2f}KB -> {file_size_after:.2f}KB ({size_reduction:.2f}% 감소)")
            
            processed_files += 1
            
        except Exception as e:
            logger.error(f"이미지 처리 오류: {filename}, {str(e)}")
    
    # 최종 결과 기록
    if total_files > 0:
        total_reduction = 100 - (total_size_after / total_size_before * 100) if total_size_before > 0 else 0
        logger.info(f"처리 완료: 총 {total_files}개 파일 중 {processed_files}개 처리됨")
        logger.info(f"총 크기: {total_size_before:.2f}KB -> {total_size_after:.2f}KB ({total_reduction:.2f}% 감소)")
    else:
        logger.warning(f"처리할 이미지 파일이 없음: {input_dir}")

def create_optimized_variants(input_dir, base_output_dir, sizes, quality=85):
    """
    다양한 크기의 최적화된 이미지 변형을 생성합니다.
    
    Args:
        input_dir: 입력 이미지 디렉토리
        base_output_dir: 기본 출력 디렉토리
        sizes: 생성할 이미지 크기 딕셔너리 {이름: (너비, 높이)}
        quality: JPEG 압축 품질 (1-100)
    """
    # 입력 디렉토리의 모든 파일 처리
    total_files = 0
    processed_files = 0
    total_size_before = 0
    total_size_after = 0
    
    # 모든 파일에 대해 반복
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        # 파일이 아니면 무시
        if not os.path.isfile(file_path):
            continue
        
        # 이미지 파일 확장자 확인
        name, ext = os.path.splitext(filename)
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
            continue
        
        # 이미지 크기 체크
        file_size_before = os.path.getsize(file_path) / 1024  # KB
        total_size_before += file_size_before
        total_files += 1
        
        try:
            # 이미지 열기
            img = Image.open(file_path)
            
            # 원본 크기 저장
            original_width, original_height = img.size
            
            # 각 크기 변형에 대해 처리
            for size_name, dimensions in sizes.items():
                target_width, target_height = dimensions
                
                # 출력 디렉토리 생성
                output_dir = os.path.join(base_output_dir, size_name)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 새 이미지 생성 (원본 복사)
                resized_img = img.copy()
                
                # 이미지 리사이징
                if target_width and target_height:
                    # 둘 다 지정된 경우
                    if size_name == "list":
                        # list용 이미지는 정확히 200x200 정사각형으로 리사이징
                        # 원본 이미지의 비율을 유지하면서 가장 작은 차원에 맞춰 조정
                        if original_width > original_height:
                            # 세로가 더 짧은 경우, 세로에 맞춰 조정 후 중앙 크롭
                            ratio = target_height / original_height
                            new_width = int(original_width * ratio)
                            resized_img = resized_img.resize((new_width, target_height), Image.LANCZOS)
                            # 가운데를 기준으로 크롭
                            left = (new_width - target_width) // 2
                            right = left + target_width
                            resized_img = resized_img.crop((left, 0, right, target_height))
                        else:
                            # 가로가 더 짧거나 같은 경우, 가로에 맞춰 조정 후 중앙 크롭
                            ratio = target_width / original_width
                            new_height = int(original_height * ratio)
                            resized_img = resized_img.resize((target_width, new_height), Image.LANCZOS)
                            # 가운데를 기준으로 크롭
                            top = (new_height - target_height) // 2
                            bottom = top + target_height
                            resized_img = resized_img.crop((0, top, target_width, bottom))
                    else:
                        # 비율 유지하면서 리사이징
                        resized_img.thumbnail((target_width, target_height), Image.LANCZOS)
                elif target_width:
                    # 너비만 지정된 경우 (비율 유지)
                    ratio = target_width / original_width
                    new_height = int(original_height * ratio)
                    resized_img = resized_img.resize((target_width, new_height), Image.LANCZOS)
                elif target_height:
                    # 높이만 지정된 경우 (비율 유지)
                    ratio = target_height / original_height
                    new_width = int(original_width * ratio)
                    resized_img = resized_img.resize((new_width, target_height), Image.LANCZOS)
                
                # 이미지 저장 경로
                output_path = os.path.join(output_dir, filename)
                
                # 이미지 포맷 결정
                img_format = 'JPEG'
                if ext.lower() == '.png':
                    img_format = 'PNG'
                elif ext.lower() == '.webp':
                    img_format = 'WEBP'
                
                # 이미지 저장
                if img_format == 'JPEG':
                    resized_img = resized_img.convert('RGB')  # JPEG는 알파 채널 지원 안함
                    resized_img.save(output_path, format=img_format, quality=quality, optimize=True)
                else:
                    resized_img.save(output_path, format=img_format, optimize=True)
                
                # 최적화 후 크기 체크
                file_size_after = os.path.getsize(output_path) / 1024
                total_size_after += file_size_after
                
                # 결과 기록
                current_width, current_height = resized_img.size
                size_reduction = 100 - (file_size_after / file_size_before * 100) if file_size_before > 0 else 0
                logger.info(f"[{size_name}] 최적화 완료: {filename}, {original_width}x{original_height} -> {current_width}x{current_height}, {file_size_before:.2f}KB -> {file_size_after:.2f}KB ({size_reduction:.2f}% 감소)")
            
            processed_files += 1
            
        except Exception as e:
            logger.error(f"이미지 처리 오류: {filename}, {str(e)}")
    
    # 최종 결과 기록
    if total_files > 0:
        total_reduction = 100 - (total_size_after / (total_size_before * len(sizes)) * 100) if total_size_before > 0 else 0
        logger.info(f"처리 완료: 총 {total_files}개 파일 중 {processed_files}개 처리됨")
        logger.info(f"총 용량 (모든 변형 포함): {total_size_before * len(sizes):.2f}KB -> {total_size_after:.2f}KB ({total_reduction:.2f}% 감소)")
    else:
        logger.warning(f"처리할 이미지 파일이 없음: {input_dir}")

if __name__ == "__main__":
    # 기본 디렉토리 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "app", "static", "images", "legislators_original")
    
    # 이미지 변형 크기 정의
    image_sizes = {
        "detail": (400, None),   # 상세 페이지용 (너비 400px, 높이 자동)
        "list": (200, 200),      # 목록 페이지용 (200x200 정사각형)
        "thumb": (40, 40)        # 썸네일용 (40x40)
    }
    
    # 각 변형 크기에 맞는 이미지 생성
    output_base_dir = os.path.join(base_dir, "app", "static", "images", "legislators_optimized")
    create_optimized_variants(input_dir, output_base_dir, image_sizes)
    
    # 기존 이미지 디렉토리 백업 (선택적)
    legislators_dir = os.path.join(base_dir, "app", "static", "images", "legislators")
    legislators_backup = os.path.join(base_dir, "app", "static", "images", "legislators_backup")
    
    # 백업 디렉토리가 없으면 생성하고 기존 이미지 백업
    if not os.path.exists(legislators_backup) and os.path.exists(legislators_dir):
        shutil.copytree(legislators_dir, legislators_backup)
        logger.info(f"기존 이미지 디렉토리 백업: {legislators_dir} -> {legislators_backup}") 