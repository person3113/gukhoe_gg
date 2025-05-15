import pandas as pd
import os
import re
from typing import List, Dict, Any

def parse_attendance_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    출석 현황 엑셀 파일을 파싱 (본회의 또는 상임위)
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    try:
        # 파일명 확인하여 본회의/상임위 구분
        filename = os.path.basename(file_path).lower()
        
        if 'plenary' in filename:
            print(f"본회의 출석 파일로 인식됨: {filename}")
            return parse_plenary_attendance_excel(file_path)
        elif 'standing' in filename:
            print(f"상임위 출석 파일로 인식됨: {filename}")
            return parse_standing_committee_attendance_excel(file_path)
        else:
            print(f"알 수 없는 출석 파일 형식: {filename}")
            # 확장자 기반 구분 시도
            try:
                # 엑셀 시트 구조 확인하여 자동 파악 시도
                xls = pd.ExcelFile(file_path)
                sheets = xls.sheet_names
                
                if '22대' in sheets:
                    print(f"시트 기반으로 본회의 출석 파일로 인식됨: {filename}")
                    return parse_plenary_attendance_excel(file_path)
                else:
                    print(f"시트 기반으로 상임위 출석 파일로 인식됨: {filename}")
                    return parse_standing_committee_attendance_excel(file_path)
            except:
                # 마지막 방법으로 파일명 대소문자 무시하고 확인
                if 'plenary' in filename.lower() or '본회의' in filename:
                    return parse_plenary_attendance_excel(file_path)
                else:
                    return parse_standing_committee_attendance_excel(file_path)
            
    except Exception as e:
        print(f"출석 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def parse_plenary_attendance_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    본회의 출석 현황 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    try:
        # 엑셀 파일 로드 (시트명: '22대')
        df = pd.read_excel(file_path, sheet_name='22대', header=None)
        
        print(f"본회의 출석 엑셀 데이터 형태: {df.shape}")
        
        # 회의 차수와 날짜 정보 추출 (3행, 4행)
        meeting_types = df.iloc[2, 2:].tolist()  # 3행 (index=2): 회의 차수
        meeting_dates = df.iloc[3, 2:].tolist()  # 4행 (index=3): 회의 날짜
        
        # 회의 날짜 형식 변환 (예: '2025년04월04일' -> '2025-04-04')
        formatted_dates = []
        for date_str in meeting_dates:
            if pd.isna(date_str):
                formatted_dates.append(None)
                continue
                
            date_str = str(date_str)
            if '년' in date_str and '월' in date_str and '일' in date_str:
                year = date_str.split('년')[0]
                month = date_str.split('년')[1].split('월')[0]
                day = date_str.split('월')[1].split('일')[0]
                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                formatted_dates.append(formatted_date)
            else:
                formatted_dates.append(None)
        
        # 결과 리스트 초기화
        attendance_data = []
        
        # 5행부터 의원 데이터 처리
        for idx, row in enumerate(df.iloc[4:].iterrows(), 5):
            row_idx, row_data = row
            
            # 의원명과 소속정당 추출
            legislator_name = row_data[0]
            party = row_data[1]
            
            # 빈 행 건너뛰기
            if pd.isna(legislator_name) or not legislator_name:
                continue
                
            # 각 의원의 회의별 출석 상태 처리
            for col_idx in range(2, len(row_data)):
                status = row_data[col_idx]
                
                # 출석 상태가 없거나 날짜가 없으면 건너뛰기
                if pd.isna(status) or not status or col_idx-2 >= len(formatted_dates) or not formatted_dates[col_idx-2]:
                    continue
                
                # 유효한 출석 상태만 처리
                if status in ["출석", "결석", "청가", "출장", "결석신고서"]:
                    attendance_record = {
                        "legislator_name": str(legislator_name).strip(),
                        "party": str(party).strip() if not pd.isna(party) else None,
                        "meeting_date": formatted_dates[col_idx-2],
                        "meeting_type": "본회의",
                        "status": str(status).strip(),
                        "committee_id": None  # 본회의는 위원회 ID가 없음
                    }
                    
                    attendance_data.append(attendance_record)
        
        print(f"본회의 출석 데이터 파싱 완료: {len(attendance_data)}개")
        return attendance_data
        
    except Exception as e:
        print(f"본회의 출석 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def parse_standing_committee_attendance_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    상임위 출석 현황 엑셀 파일을 파싱
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    try:
        # 결과 리스트 초기화
        attendance_data = []
        
        # 엑셀 시트 목록 가져오기
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        
        # 연도 추출 (파일명에서 추출)
        filename = os.path.basename(file_path)
        year = None
        if '_' in filename:
            year_part = filename.split('_')[0]
            if year_part.isdigit() and len(year_part) == 4:
                year = year_part
        
        print(f"상임위 출석 엑셀 파일: {filename}, 시트 수: {len(sheets)}")
        
        # 각 시트(위원회별) 처리
        for sheet_name in sheets:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # 위원회 이름 추출 (A1 셀)
                committee_name = df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else None
                if not committee_name:
                    print(f"  - 시트 '{sheet_name}'에서 위원회 이름을 찾을 수 없음, 건너뜀")
                    continue
                
                print(f"  - 시트 '{sheet_name}' 처리 중: {committee_name}")
                
                # 회의 날짜와 차수 찾기 (주로 3행과 4행에 있음)
                meeting_dates_row = None
                meeting_types_row = None
                
                # 회의일자와 회의차수 행 찾기
                for i in range(10):  # 처음 10행 내에서 찾기
                    row_data = df.iloc[i, :].tolist()
                    row_str = str(row_data).lower()
                    
                    if any(keyword in row_str for keyword in ['회의일자', '회의일']):
                        meeting_dates_row = i
                    elif any(keyword in row_str for keyword in ['차', '회의차수']):
                        meeting_types_row = i
                
                if meeting_dates_row is None or meeting_types_row is None:
                    print(f"  - 시트 '{sheet_name}'에서 회의일자/차수 행을 찾을 수 없음, 기본값 사용")
                    meeting_dates_row = 3  # 기본값: 4행 (index=3)
                    meeting_types_row = 4  # 기본값: 5행 (index=4)
                
                # 회의 날짜 추출 및 형식 변환
                meeting_dates = []
                for col in range(1, df.shape[1]):
                    date_val = df.iloc[meeting_dates_row, col]
                    if pd.isna(date_val):
                        meeting_dates.append(None)
                        continue
                    
                    date_str = str(date_val)
                    # 다양한 날짜 형식 처리
                    formatted_date = None
                    
                    if '월' in date_str and '일' in date_str:
                        # 만약 연도가 없는 경우 파일명에서 추출한 연도 사용
                        if '년' in date_str:
                            # '2024년 6월 18일' 또는 '2024년06월18일' 형식
                            year_part = date_str.split('년')[0].strip()
                            month_part = date_str.split('년')[1].split('월')[0].strip()
                            day_part = date_str.split('월')[1].split('일')[0].strip()
                        else:
                            # '6월 18일' 형식 - 연도는 파일명에서 추출
                            if year:
                                year_part = year
                            else:
                                year_part = "2024"  # 기본값
                            month_part = date_str.split('월')[0].strip()
                            day_part = date_str.split('월')[1].split('일')[0].strip()
                        
                        # 숫자만 추출
                        import re
                        year_part = re.sub(r'[^0-9]', '', year_part)
                        month_part = re.sub(r'[^0-9]', '', month_part)
                        day_part = re.sub(r'[^0-9]', '', day_part)
                        
                        if year_part and month_part and day_part:
                            formatted_date = f"{year_part}-{month_part.zfill(2)}-{day_part.zfill(2)}"
                    
                    meeting_dates.append(formatted_date)
                
                # 의원 데이터 시작 행 찾기 (보통 6행부터 시작)
                data_start_row = 5  # 기본값: 6행 (index=5)
                
                # 의원 데이터 처리
                for idx, row in enumerate(df.iloc[data_start_row:].iterrows(), data_start_row):
                    row_idx, row_data = row
                    
                    # 의원명 추출 (A열)
                    legislator_name = row_data[0]
                    
                    # 빈 행 건너뛰기
                    if pd.isna(legislator_name) or not legislator_name:
                        continue
                    
                    # '회의일수', '출석', '결석' 등 요약행 건너뛰기
                    if any(keyword in str(legislator_name).lower() for keyword in ['회의일수', '출석합계', '합계']):
                        continue
                    
                    # 각 열의 출석 상태 처리
                    for col_idx in range(1, len(row_data)):
                        status = row_data[col_idx]
                        
                        # 출석 상태가 없거나 날짜가 없으면 건너뛰기
                        if pd.isna(status) or not status or col_idx-1 >= len(meeting_dates) or not meeting_dates[col_idx-1]:
                            continue
                        
                        # 유효한 출석 상태만 처리
                        if str(status).strip() in ["출석", "결석", "청가", "출장", "결석신고서"]:
                            attendance_record = {
                                "legislator_name": str(legislator_name).strip(),
                                "committee_name": str(committee_name).strip(),
                                "meeting_date": meeting_dates[col_idx-1],
                                "meeting_type": "상임위",
                                "status": str(status).strip()
                            }
                            
                            attendance_data.append(attendance_record)
            
            except Exception as e:
                print(f"  - 시트 '{sheet_name}' 처리 중 오류 발생: {str(e)}")
                continue
        
        print(f"상임위 출석 데이터 파싱 완료: {len(attendance_data)}개")
        return attendance_data
        
    except Exception as e:
        print(f"상임위 출석 엑셀 파일 파싱 오류 ({file_path}): {str(e)}")
        import traceback
        traceback.print_exc()
        return []

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