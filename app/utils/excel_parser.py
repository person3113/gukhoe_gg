import pandas as pd
from typing import List, Dict, Any

def parse_attendance_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    출석 현황 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    # 호출: pandas.read_excel()로 출석 현황 엑셀 파일 읽기
    # 데이터 클리닝 및 구조화
    # 반환: 출석 데이터 리스트
    pass

def parse_speech_keywords_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    발언 키워드 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 키워드 데이터 리스트
    """
    try:
        # 명세서에 따르면:
        # - 시트명: "발언 키워드 Top10"
        # - 헤더는 3번째 행 (header=2)
        # - 컬럼: 발언자, 키워드, 키워드수
        
        # 시트2 "발언 키워드 Top10"에서 데이터 읽기
        df_keywords = pd.read_excel(file_path, sheet_name="발언 키워드 Top10", header=2)
        
        # 데이터 확인
        print(f"엑셀 데이터 형태: {df_keywords.shape}")
        print(f"컬럼명: {df_keywords.columns.tolist()}")
        
        if not df_keywords.empty:
            print(f"첫 5행 데이터 샘플:")
            print(df_keywords.head())
        
        # 결과 데이터 생성
        result = []
        
        for _, row in df_keywords.iterrows():
            # 행 데이터가 유효한지 확인
            if pd.isna(row['발언자']) or pd.isna(row['키워드']):
                continue
            
            keyword_data = {
                'legislator_name': str(row['발언자']).strip(),
                'keyword': str(row['키워드']).strip(),
                'count': int(row['키워드수']) if pd.notna(row['키워드수']) else 0
            }
            result.append(keyword_data)
        
        print(f"파싱 완료: {len(result)}개의 키워드 데이터")
        return result
        
    except Exception as e:
        print(f"키워드 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def parse_speech_by_meeting_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    회의별 발언 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 회의별 발언 데이터 리스트
    """
    # 호출: pandas.read_excel()로 회의별 발언 엑셀 파일 읽기
    # 데이터 클리닝 및 구조화
    # 반환: 회의별 발언 데이터 리스트
    # pandas.read_excel()로 회의별 발언 엑셀 파일 읽기
    """
    회의별 발언 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 회의별 발언 데이터 리스트
    """
    try:
        # 두 번째 시트('대수 회의구분별 통계')를 읽기
        df = pd.read_excel(file_path, sheet_name=1, header=None)
        
        # 데이터 확인 및 디버깅
        print(f"엑셀 데이터 형태: {df.shape}")
        if not df.empty:
            print(f"첫 5행 데이터 샘플:")
            print(df.head())
        
        # 헤더 정보 설정
        headers = ['발언자', '대수', '회의구분', '회의록수']
        
        # 데이터 시작 행 찾기
        header_row = None
        data_start_row = None
        
        for i in range(min(10, len(df))):
            if pd.notna(df.iloc[i, 0]) and df.iloc[i, 0] == '발언자':
                header_row = i
                data_start_row = i + 1
                break
        
        if header_row is None:
            print(f"경고: '발언자' 헤더를 찾을 수 없습니다. 기본값 사용")
            header_row = 0
            data_start_row = 1
        
        print(f"헤더 행: {header_row}, 데이터 시작 행: {data_start_row}")
        
        # 데이터 파싱
        data_df = df.iloc[data_start_row:].copy()
        data_df.columns = headers
        
        # NaN 또는 빈 값 확인 및 필터링
        data_df = data_df.dropna(subset=['발언자', '회의구분'])
        
        # === 22대 국회 데이터만 필터링 ===
        result = []
        
        for _, row in data_df.iterrows():
            # 행 데이터가 유효한지 확인
            if pd.isna(row['발언자']) or not row['발언자']:
                continue
            
            # 대수 확인 - 22대만 처리
            try:
                assembly_no = int(row['대수']) if pd.notna(row['대수']) else 0
            except (ValueError, TypeError):
                assembly_no = 0
                
            # 22대가 아니면 건너뛰기
            if assembly_no != 22:
                print(f"  - {assembly_no}대 데이터 건너뜀: {row['발언자']} - {row['회의구분']}")
                continue
            
            # '회의록수' 필드 처리
            count = 0
            if pd.notna(row['회의록수']):
                try:
                    count = int(row['회의록수'])
                except (ValueError, TypeError):
                    print(f"경고: 회의록수 '{row['회의록수']}'를 숫자로 변환할 수 없습니다. 기본값 0 사용")
            
            # 'Total' 확인
            is_total = False
            if isinstance(row['회의구분'], str) and row['회의구분'].strip() == 'Total':
                is_total = True
                
            speech_data = {
                'legislator_name': str(row['발언자']),
                'assembly_no': assembly_no,
                'meeting_type': 'Total' if is_total else str(row['회의구분']),
                'count': count
            }
            result.append(speech_data)
            print(f"  - 22대 데이터 추가: {speech_data['legislator_name']} - {speech_data['meeting_type']}: {speech_data['count']}")
        
        print(f"\n파싱 완료: 22대 데이터 {len(result)}개")
        return result
    except Exception as e:
        print(f"회의별 발언 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []