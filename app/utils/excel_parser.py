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
    try:
        # 두 번째 시트('대수 회의구분별 통계')를 읽기 - 데이터는 2행부터 시작
        df = pd.read_excel(file_path, sheet_name=1, header=None)
        
        # 2행(인덱스 1)에 있는 헤더 정보를 가져옴
        headers = ['발언자', '대수', '회의구분', '회의록수']
        
        # 3행부터 데이터 시작
        data_df = df.iloc[2:].copy()
        data_df.columns = headers
        
        # 결과 리스트 생성
        result = []
        for _, row in data_df.iterrows():
            speech_data = {
                'legislator_name': row['발언자'],
                'assembly_no': row['대수'],
                'meeting_type': row['회의구분'],
                'count': int(row['회의록수']) if not pd.isna(row['회의록수']) else 0
            }
            result.append(speech_data)
            
        return result
    except Exception as e:
        print(f"엑셀 파일 파싱 오류: {str(e)}")
        return []