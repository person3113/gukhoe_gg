import sys
import os
import pandas as pd

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def debug_excel_headers():
    """모든 상임위 엑셀 파일의 헤더 구조 확인"""
    standing_dir = "data/excel/attendance/standing_committee"
    
    if not os.path.exists(standing_dir):
        print(f"폴더가 존재하지 않습니다: {standing_dir}")
        return
    
    files = [f for f in os.listdir(standing_dir) if f.endswith('.xlsx')]
    
    for filename in files:
        file_path = os.path.join(standing_dir, filename)
        print(f"\n=== 파일: {filename} ===")
        
        try:
            xls = pd.ExcelFile(file_path)
            
            # 문제가 되는 시트 7부터 체크
            for sheet_idx, sheet_name in enumerate(xls.sheet_names):
                if sheet_idx >= 6:  # Sheet7부터
                    print(f"\n--- 시트: {sheet_name} (인덱스: {sheet_idx}) ---")
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    
                    print(f"위원회명: {df.iloc[0, 0]}")
                    
                    # 0~5행까지의 모든 데이터 표시
                    for i in range(min(6, len(df))):
                        row_values = df.iloc[i].tolist()
                        non_empty = [f"{j}:{v}" for j, v in enumerate(row_values) if pd.notna(v)]
                        print(f"행 {i}: {non_empty}")
                    
                    # 헤더로 보이는 행 찾기
                    for i in range(min(10, len(df))):
                        row_values = df.iloc[i].tolist()
                        row_str = ' '.join(str(v) for v in row_values if pd.notna(v))
                        if any(keyword in row_str for keyword in ['회의일수', '출석', '결석']):
                            print(f"헤더 발견 (행 {i}): {[v for v in row_values if pd.notna(v)]}")
                            
        except Exception as e:
            print(f"파일 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_excel_headers()