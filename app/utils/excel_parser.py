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
    """
    회의록별 발언수 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        Dict[str, Any]: {'total': int, 'by_meeting': List[Dict]} 형태로 반환
    """
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path, header=None)
        
        # 두 번째 행(인덱스 1)을 헤더로 설정
        headers = df.iloc[1].tolist()
        df.columns = headers
        
        # 데이터는 3번째 행부터 시작 (인덱스 2)
        df = df[2:].reset_index(drop=True)
        
        result = {
            'total': 0,  # Total 값 (의정발언 점수 계산용)
            'by_meeting': []  # 회의구분별 발언수
        }
        
        for _, row in df.iterrows():
            meeting_type = row['회의구분']
            count = int(row['회의록수']) if row['회의록수'] else 0
            
            if meeting_type == 'Total':
                result['total'] = count
            else:
                speech_data = {
                    'meeting_type': meeting_type,
                    'count': count
                }
                result['by_meeting'].append(speech_data)
        
        return result
        
    except Exception as e:
        print(f"엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        return {'total': 0, 'by_meeting': []}