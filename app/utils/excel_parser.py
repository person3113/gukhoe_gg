import pandas as pd
from typing import List, Dict, Any
import os
import glob

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
    회의별 발언 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 회의별 발언 데이터 리스트
    """
    try:
        import pandas as pd
        import os
        
        print(f"파싱 중인 파일: {os.path.basename(file_path)}")
        
        # 헤더 없이 파일 읽기
        df = pd.read_excel(file_path, header=None)
        
        # 데이터 구조 확인
        print(f"데이터 형태: {df.shape}")
        
        # 처음 몇 행 출력하여 구조 확인
        print("파일 구조 샘플:")
        print(df.head())
        
        # 2행(인덱스 1)을 헤더로 사용 - 실제 파일에서 확인
        header_row = df.iloc[1]
        print("헤더 행:", header_row.tolist())
        
        # 헤더 정의 - 파일에서 추출 또는 고정된 헤더 사용
        # 파일 구조가 변경될 경우 대비하여 컬럼 위치 확인
        expected_headers = ['발언자', '대수', '회의구분', '회의록수']
        actual_headers = [str(col) for col in header_row.tolist() if not pd.isna(col)]
        
        # 헤더 일치 여부 확인
        print(f"예상 헤더: {expected_headers}")
        print(f"실제 헤더: {actual_headers}")
        
        # 헤더 매핑 (인덱스 기반으로 헤더 이름 매핑)
        headers = []
        for i, header in enumerate(header_row):
            if i < len(expected_headers) and not pd.isna(header):
                headers.append(expected_headers[i])
            else:
                headers.append(f"Unnamed: {i}")
        
        # 실제 데이터만 추출 (2행 이후)
        data_df = df.iloc[2:].reset_index(drop=True)
        
        # 컬럼명 설정
        data_df.columns = headers
        
        print("헤더 적용 후 데이터:")
        print(data_df.head())
        
        # 결과 리스트 초기화
        result = []
        
        # 데이터 행 처리
        for idx, row in data_df.iterrows():
            legislator_name = row['발언자']
            meeting_type = row['회의구분']
            count = row['회의록수']
            
            # 값이 비어있거나 NaN인 경우 건너뛰기
            if pd.isna(legislator_name) or pd.isna(meeting_type) or pd.isna(count):
                continue
            
            # 의원 이름에서 한자 부분 제거 (예: "강경숙 (姜景淑)" -> "강경숙")
            if '(' in legislator_name:
                legislator_name = legislator_name.split('(')[0].strip()
            
            # 숫자형으로 변환 (문자열이나 NaN 방지)
            try:
                count = int(count)
            except (ValueError, TypeError):
                count = 0
            
            # Total이 아닌 경우만 저장 (Total은 합계이므로 개별 저장 불필요)
            if str(meeting_type) != 'Total':
                # 결과 딕셔너리에 추가
                result.append({
                    "legislator_name": legislator_name,
                    "meeting_type": meeting_type,
                    "count": count
                })
        
        print(f"처리된 데이터 수: {len(result)}")
        
        # 데이터 샘플 출력
        if result:
            print("데이터 샘플:")
            for i, item in enumerate(result[:3]):
                print(f"  {i+1}. {item['legislator_name']} - {item['meeting_type']}: {item['count']}회")
        
        return result
    
    except Exception as e:
        print(f"회의별 발언 엑셀 파일 파싱 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return []