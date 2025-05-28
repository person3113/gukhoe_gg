import os
import sys
from PIL import Image
import logging

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
            file_size_after = os.path.getsize(output_path) / 1024  # KB
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

if __name__ == "__main__":
    # 실행 인자 처리
    if len(sys.argv) < 3:
        print("사용법: python optimize_images.py <입력_디렉토리> <출력_디렉토리> [최대_너비] [품질]")
        print("기본값: 최대_너비=800, 품질=85")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    max_width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 85
    
    # 입력 디렉토리 확인
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        logger.error(f"입력 디렉토리가 존재하지 않음: {input_dir}")
        sys.exit(1)
    
    # 이미지 최적화 실행
    optimize_images(input_dir, output_dir, max_width, quality) 