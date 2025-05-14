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
        
        # 헤더 정보 설정
        headers = ['발언자', '대수', '회의구분', '회의록수']
        
        # 데이터 시작 행 - 먼저 발언자가 있는 행을 찾아야 함
        # 대부분 3행(인덱스 2)부터 시작이지만, 파일마다 다를 수 있음
        data_start_row = 2  # 기본값
        
        # 첫 번째 열에 '발언자'가 있는 행 찾기
        for i in range(len(df)):
            if isinstance(df.iloc[i, 0], str) and df.iloc[i, 0] != '발언자' and df.iloc[i, 0]:
                data_start_row = i
                break
        
        # 데이터 파싱
        data_df = df.iloc[data_start_row:].copy()
        data_df.columns = headers
        
        # 결과 리스트 생성
        result = []
        has_total = False  # Total 데이터 존재 여부 확인
        
        for _, row in data_df.iterrows():
            # 행 데이터가 유효한지 확인
            if pd.isna(row['발언자']) or not row['발언자']:
                continue
                
            # 'Total' 데이터 확인
            is_total = False
            if isinstance(row['회의구분'], str) and row['회의구분'].strip() == 'Total':
                is_total = True
                has_total = True
                
            speech_data = {
                'legislator_name': row['발언자'],
                'assembly_no': int(row['대수']) if not pd.isna(row['대수']) else 22,  # 기본값 22
                'meeting_type': 'Total' if is_total else row['회의구분'],
                'count': int(row['회의록수']) if not pd.isna(row['회의록수']) else 0
            }
            result.append(speech_data)
        
        # Total 데이터가 없는 경우, 다른 회의 구분의 합으로 계산하여 추가
        if not has_total:
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
            
        return result
    except Exception as e:
        print(f"회의별 발언 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        return []