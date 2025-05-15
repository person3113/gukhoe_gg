import sys
import os
import pandas as pd

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_excel_structure(file_path):
    """엑셀 파일의 구조를 확인"""
    try:
        print(f"\n=== 파일: {os.path.basename(file_path)} ===")
        
        # 시트 목록 확인
        xls = pd.ExcelFile(file_path)
        print(f"시트 목록: {xls.sheet_names}")
        
        # 각 시트의 구조 확인
        for sheet_name in xls.sheet_names[:1]:  # 첫 번째 시트만 상세 확인
            print(f"\n--- 시트: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            print(f"데이터 크기: {df.shape}")
            print("\n처음 10행, 10열:")
            print(df.iloc[:10, :10])
            
            # 헤더로 보이는 행 찾기
            for i in range(min(10, len(df))):
                row_values = df.iloc[i].tolist()
                # 공백이 아닌 값들만 표시
                non_empty = [str(val) for val in row_values if pd.notna(val)]
                if non_empty:
                    print(f"\n행 {i}: {non_empty[:10]}...")  # 처음 10개만
                    
                    # 가능한 헤더 행 찾기
                    if any(keyword in str(non_empty) for keyword in ['의원명', '위원명', '출석', '결석']):
                        print(f"  → 가능한 헤더 행!")
                    
                    # 가능한 데이터 시작 행 찾기
                    if i > 2:  # 헤더 이후
                        first_val = str(row_values[0]) if pd.notna(row_values[0]) else ""
                        if first_val and '위원' not in first_val and '의원' not in first_val:
                            print(f"  → 가능한 데이터 시작 행!")
                            # 이 행의 값들 상세 확인
                            print(f"  → 행 데이터: {[f'{i}:{v}' for i, v in enumerate(row_values[:10]) if pd.notna(v)]}")
            
    except Exception as e:
        print(f"파일 확인 중 오류: {e}")
        import traceback
        traceback.print_exc()

def main():
    """메인 함수"""
    # 상임위 파일 확인
    standing_dir = "data/excel/attendance/standing_committee"
    
    if not os.path.exists(standing_dir):
        print(f"폴더가 존재하지 않습니다: {standing_dir}")
        return
    
    files = [f for f in os.listdir(standing_dir) if f.endswith('.xlsx')]
    
    if not files:
        print("확인할 파일이 없습니다.")
        return
    
    # 첫 번째 파일 상세 확인
    first_file = os.path.join(standing_dir, files[0])
    check_excel_structure(first_file)
    
    # 특정 인덱스 위치의 데이터 타입 확인
    print("\n=== 데이터 타입 확인 ===")
    try:
        df = pd.read_excel(first_file, sheet_name=0, header=None)
        
        # 문제가 되는 위치들 확인
        if len(df) > 5 and len(df.columns) > 8:
            print(f"\n위치 [5, 3]: {df.iloc[5, 3]} (타입: {type(df.iloc[5, 3])})")
            print(f"위치 [5, 4]: {df.iloc[5, 4]} (타입: {type(df.iloc[5, 4])})")
            print(f"위치 [5, 5]: {df.iloc[5, 5]} (타입: {type(df.iloc[5, 5])})")
            print(f"위치 [5, 6]: {df.iloc[5, 6]} (타입: {type(df.iloc[5, 6])})")
            print(f"위치 [5, 7]: {df.iloc[5, 7]} (타입: {type(df.iloc[5, 7])})")
            print(f"위치 [5, 8]: {df.iloc[5, 8]} (타입: {type(df.iloc[5, 8])})")
    except Exception as e:
        print(f"데이터 타입 확인 중 오류: {e}")

if __name__ == "__main__":
    main()