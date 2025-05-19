# scripts/check_excel_data.py
import sys
import os
import pandas as pd

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_excel_content():
    """
    엑셀 파일의 내용을 확인하는 함수
    """
    # 파일 경로 설정
    asset_dir = os.path.join('data', 'excel', 'asset')
    
    # 지정된 파일명 확인
    expected_file = 'asset_2025_03.xlsx'
    file_path = os.path.join(asset_dir, expected_file)
    
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        # 디렉토리 내의 다른 엑셀 파일 확인
        excel_files = [f for f in os.listdir(asset_dir) if f.endswith('.xlsx') or f.endswith('.xls')]
        if excel_files:
            print(f"대신 다음 엑셀 파일을 찾았습니다: {excel_files}")
            # 첫 번째 찾은 파일 사용
            file_path = os.path.join(asset_dir, excel_files[0])
            print(f"파일 사용: {file_path}")
        else:
            print(f"디렉토리에 엑셀 파일이 없습니다: {asset_dir}")
            return
    
    # 엑셀 파일 읽기
    df = pd.read_excel(file_path)
    
    # 파일 기본 정보 출력
    print(f"엑셀 파일 크기: {df.shape}")
    print(f"컬럼 목록: {df.columns.tolist()}")
    
    # 소재지 컬럼 존재 여부 확인
    if '소재지' in df.columns:
        print("\n소재지 컬럼이 존재합니다.")
        
        # 소재지 값의 타입과 내용 확인
        print("\n첫 10개 행의 소재지 값 확인:")
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            if idx > 10:
                break
                
            location = row.get('소재지')
            location_type = type(location).__name__
            location_str = str(location)
            is_nan = pd.isna(location)
            
            print(f"행 {idx}: 값='{location}', 타입={location_type}, 문자열='{location_str}', NaN={is_nan}")
    else:
        print("\n소재지 컬럼이 존재하지 않습니다. 유사한 컬럼 검색:")
        
        # 유사한 이름의 컬럼 검색
        similar_columns = [col for col in df.columns if '소재' in col or '위치' in col or '주소' in col]
        print(f"  유사한 컬럼: {similar_columns}")
    
    # 우원식 의원 데이터 확인
    if '이름' in df.columns:
        woo_data = df[df['이름'] == '우원식']
        if not woo_data.empty:
            print(f"\n우원식 의원 데이터 {len(woo_data)}건 발견")
            
            # 우원식 의원의 소재지 정보 확인
            if '소재지' in df.columns:
                print("\n우원식 의원의 소재지 정보:")
                for idx, (_, row) in enumerate(woo_data.iterrows(), 1):
                    asset_type = row.get('재산의종류', '정보 없음')
                    location = row.get('소재지', '정보 없음')
                    print(f"{idx}. {asset_type}: 소재지='{location}'")

if __name__ == "__main__":
    check_excel_content()