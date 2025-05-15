# scripts/check_plenary_structure.py
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_plenary_structure():
    """본회의 엑셀 파일의 구조 확인"""
    plenary_dir = "data/excel/attendance/plenary"
    files = [f for f in os.listdir(plenary_dir) if f.endswith('.xlsx')]
    
    if not files:
        print("본회의 파일이 없습니다.")
        return
    
    file_path = os.path.join(plenary_dir, files[0])
    print(f"파일: {files[0]}")
    
    # 엑셀 파일 로드
    df = pd.read_excel(file_path, sheet_name='22대', header=None)
    
    print(f"\n데이터 형태: {df.shape}")
    
    # 처음 10행, 25열까지 표시
    print("\n처음 10행, 25열 데이터:")
    for i in range(min(10, len(df))):
        row_data = df.iloc[i].tolist()[:25]
        non_empty = [f"{j}:{v}" for j, v in enumerate(row_data) if pd.notna(v)]
        print(f"행 {i}: {non_empty}")
    
    # 특정 의원의 데이터 확인
    print("\n특정 의원 데이터 확인:")
    for i in range(4, min(7, len(df))):
        row_data = df.iloc[i].tolist()
        if pd.notna(row_data[0]):
            print(f"\n의원: {row_data[0]}")
            print(f"전체 행 데이터: {[f'{j}:{v}' for j, v in enumerate(row_data) if pd.notna(v)]}")

if __name__ == "__main__":
    check_plenary_structure()