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
    # 호출: pandas.read_excel()로 발언 키워드 엑셀 파일 읽기
    # 데이터 클리닝 및 구조화
    # 반환: 키워드 데이터 리스트
    pass

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
        
        # 데이터 시작 행 찾기 - 첫 번째 열에 '발언자'가 있는 행을 찾고, 그 다음 행부터 데이터로 간주
        header_row = None
        data_start_row = None
        
        for i in range(min(10, len(df))):  # 처음 10행만 확인
            if pd.notna(df.iloc[i, 0]) and df.iloc[i, 0] == '발언자':
                header_row = i
                data_start_row = i + 1
                break
        
        # 헤더를 찾지 못한 경우
        if header_row is None:
            print(f"경고: '발언자' 헤더를 찾을 수 없습니다. 기본값 사용")
            # 첫 번째 행이 헤더라고 가정
            header_row = 0
            data_start_row = 1
        
        print(f"헤더 행: {header_row}, 데이터 시작 행: {data_start_row}")
        
        # 데이터 파싱
        data_df = df.iloc[data_start_row:].copy()
        data_df.columns = headers
        
        # NaN 또는 빈 값 확인 및 필터링
        data_df = data_df.dropna(subset=['발언자', '회의구분'])
        
        # 결과 리스트 생성
        result = []
        has_total = False  # Total 데이터 존재 여부 확인
        
        for _, row in data_df.iterrows():
            # 행 데이터가 유효한지 확인
            if pd.isna(row['발언자']) or not row['발언자']:
                continue
            
            # '대수' 필드가 숫자인지 확인, 아니면 기본값 22 사용
            assembly_no = 22  # 기본값
            if pd.notna(row['대수']):
                try:
                    assembly_no = int(row['대수'])
                except (ValueError, TypeError):
                    # 변환 실패 시 기본값 사용
                    print(f"경고: 대수 '{row['대수']}'를 숫자로 변환할 수 없습니다. 기본값 22 사용")
            
            # '회의록수' 필드가 숫자인지 확인, 아니면 기본값 0 사용
            count = 0  # 기본값
            if pd.notna(row['회의록수']):
                try:
                    count = int(row['회의록수'])
                except (ValueError, TypeError):
                    # 변환 실패 시 기본값 사용
                    print(f"경고: 회의록수 '{row['회의록수']}'를 숫자로 변환할 수 없습니다. 기본값 0 사용")
            
            # 'Total' 데이터 확인
            is_total = False
            if isinstance(row['회의구분'], str) and row['회의구분'].strip() == 'Total':
                is_total = True
                has_total = True
                
            speech_data = {
                'legislator_name': str(row['발언자']),
                'assembly_no': assembly_no,
                'meeting_type': 'Total' if is_total else str(row['회의구분']),
                'count': count
            }
            result.append(speech_data)
        
        # Total 데이터가 없는 경우, 다른 회의 구분의 합으로 계산하여 추가
        if not has_total and result:
            print(f"  - 'Total' 데이터가 없어 자동 계산됨 ({file_path})")
            
            # 의원별 발언 합계 계산
            legislator_totals = {}
            for data in result:
                name = data['legislator_name']
                if name not in legislator_totals:
                    legislator_totals[name] = 0
                legislator_totals[name] += data['count']
            
            # Total 데이터 추가
            for name, count in legislator_totals.items():
                result.append({
                    'legislator_name': name,
                    'assembly_no': 22,  # 기본값
                    'meeting_type': 'Total',
                    'count': count
                })
        
        print(f"파싱 완료: {len(result)}개의 데이터")
        return result
    except Exception as e:
        print(f"회의별 발언 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []