# scripts/explore_speech_headers.py
import pandas as pd
from pathlib import Path

def explore_speech_headers():
    """
    헤더 정보를 더 자세히 확인
    """
    speech_dir = Path("data/excel/speech")
    sample_folder = list(speech_dir.iterdir())[0]
    excel_files = list(sample_folder.glob("*전체+회의+구분별+발언+회의록+수.xlsx"))
    
    if not excel_files:
        print("파일을 찾을 수 없습니다.")
        return
    
    sample_file = excel_files[0]
    
    # 대수 회의구분별 통계 시트 읽기
    df_raw = pd.read_excel(sample_file, sheet_name='대수 회의구분별 통계')
    
    print("=== 원본 데이터 첫 5행 ===")
    print(df_raw.iloc[:5])
    
    # 2행(인덱스 1)이 실제 헤더인 것 같음
    print("\n=== 2행(인덱스 1)의 데이터 ===")
    print(df_raw.iloc[1])
    
    # 2행을 헤더로 사용해서 다시 읽기
    df_custom = pd.read_excel(sample_file, sheet_name='대수 회의구분별 통계', skiprows=1)
    
    # 첫 번째 행을 새로운 헤더로 설정
    df_custom.columns = df_custom.iloc[0]
    df_custom = df_custom.drop(0).reset_index(drop=True)
    
    print("\n=== 헤더 적용 후 ===")
    print(f"컬럼명: {df_custom.columns.tolist()}")
    print("\n데이터:")
    print(df_custom)
    
    # 회의구분별 발언 회의록수 확인
    print("\n=== 회의구분별 데이터 ===")
    for idx, row in df_custom.iterrows():
        print(f"발언자: {row['발언자']}, 회의구분: {row['회의구분']}, 회의록수: {row['회의록수']}")

if __name__ == "__main__":
    explore_speech_headers()