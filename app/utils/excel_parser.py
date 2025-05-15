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
        
        # 결과 리스트 초기화
        attendance_data = []
        
        # 22대 총계 데이터만 파싱하도록 변경
        for idx, row in enumerate(df.iloc[4:].iterrows(), 5):
            row_idx, row_data = row
            
            # 의원명 추출
            legislator_name = row_data[0]
            
            # 빈 행 건너뛰기
            if pd.isna(legislator_name) or not legislator_name:
                continue
            
            # 실제 22대 총계 데이터 위치 (15~20열)
            total_days = row_data[15] if pd.notna(row_data[15]) else 0  # 회의일수
            attended = row_data[16] if pd.notna(row_data[16]) else 0    # 출석
            absent = row_data[17] if pd.notna(row_data[17]) else 0      # 결석
            leave = row_data[18] if pd.notna(row_data[18]) else 0       # 청가
            trip = row_data[19] if pd.notna(row_data[19]) else 0        # 출장
            report = row_data[20] if pd.notna(row_data[20]) else 0      # 결석신고서
            
            # 각 상태별로 데이터 생성
            statuses = [
                ("회의일수", total_days),
                ("출석", attended),
                ("결석", absent),
                ("청가", leave),
                ("출장", trip),
                ("결석신고서", report)
            ]
            
            # 각 출석 상태별로 데이터 생성
            for status, count in statuses:
                attendance_data.append({
                    "legislator_name": str(legislator_name).strip(),
                    "meeting_type": "본회의",
                    "status": status,
                    "count": int(count),
                    "committee_id": None
                })
        
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
        attendance_data = []
        
        # 엑셀 시트 목록 가져오기
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        
        # 각 시트(위원회별) 처리
        for sheet_idx, sheet_name in enumerate(sheets):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # 위원회 이름 추출 (A1 셀)
                committee_name = df.iloc[0, 0] if not pd.isna(df.iloc[0, 0]) else None
                if not committee_name:
                    continue
                
                print(f"  - 시트 '{sheet_name}' 처리 중: {committee_name}")
                
                # 헤더 행 동적으로 찾기
                header_row = None
                data_start_row = None
                
                for i in range(2, min(10, len(df))):
                    row_values = df.iloc[i].tolist()
                    row_str = ' '.join(str(v) for v in row_values if pd.notna(v))
                    
                    # 헤더행 조건: "회의일수", "출석", "결석" 중 2개 이상 포함
                    header_keywords = ['회의일수', '출석', '결석']
                    matched_keywords = sum(1 for keyword in header_keywords if keyword in row_str)
                    
                    if matched_keywords >= 2:
                        header_row = i
                        
                        # 헤더 이후 실제 데이터가 있는 행 찾기
                        for j in range(i+1, min(i+10, len(df))):
                            test_row = df.iloc[j].tolist()
                            if pd.notna(test_row[0]):
                                first_val = str(test_row[0])
                                # 한자가 포함된 의원명 패턴 확인
                                if '(' in first_val and ')' in first_val:
                                    data_start_row = j
                                    break
                                # 또는 한글로만 된 의원명
                                elif any(ord('가') <= ord(char) <= ord('힣') for char in first_val):
                                    # 날짜나 차수 관련 단어가 없는 경우
                                    if not any(word in first_val for word in ['일', '차', '제', '회']):
                                        data_start_row = j
                                        break
                        break
                
                if header_row is None:
                    print(f"  - 시트 '{sheet_name}'에서 헤더 행을 찾을 수 없음")
                    continue
                
                if data_start_row is None:
                    print(f"  - 시트 '{sheet_name}'에서 데이터 시작 행을 자동으로 찾을 수 없음")
                    # 헤더 이후 3행부터 시작하도록 기본값 설정
                    data_start_row = header_row + 3
                
                print(f"  - 헤더 행: {header_row}, 데이터 시작 행: {data_start_row}")
                
                # 헤더 분석
                header = df.iloc[header_row].tolist()
                
                # 헤더에서 요약 데이터 열 인덱스 찾기
                indices = {
                    'meeting_days': None,  # 회의일수
                    'attended': None,      # 출석
                    'absent': None,        # 결석
                    'leave': None,         # 청가서
                    'trip': None,          # 출장
                    'report': None         # 결석신고서
                }
                
                for i, col in enumerate(header):
                    if pd.notna(col):
                        # 공백 제거하고 비교
                        col_str = str(col).strip().replace(' ', '')
                        if "회의일수" in col_str:
                            indices['meeting_days'] = i
                        elif col_str == "출석":
                            indices['attended'] = i
                        elif col_str == "결석":
                            indices['absent'] = i
                        elif "청가" in col_str:  # 청가서, 청가, 청 가서 모두 포함
                            indices['leave'] = i
                        elif col_str == "출장":
                            indices['trip'] = i
                        elif "결석신고서" in col_str:
                            indices['report'] = i
                
                if indices['meeting_days'] is None:
                    print(f"  - 시트 '{sheet_name}'에서 회의일수 열을 찾을 수 없음")
                    continue
                
                # 의원별 출석 요약 데이터 처리
                for idx, row in enumerate(df.iloc[data_start_row:].iterrows(), data_start_row):
                    row_idx, row_data = row
                    
                    # 의원명 추출 (A열)
                    legislator_name = row_data[0]
                    
                    # 빈 행이나 요약행 건너뛰기
                    if pd.isna(legislator_name) or not legislator_name:
                        continue
                    
                    legislator_name_str = str(legislator_name).strip()
                    if any(keyword in legislator_name_str.lower() for keyword in ['합계', '계', '소계', '총계']):
                        continue
                    
                    # 의원명에서 한자 제거
                    if '(' in legislator_name_str:
                        legislator_name_str = legislator_name_str.split('(')[0].strip()
                    
                    # 요약 데이터 추출
                    statuses = []
                    
                    for key, idx in indices.items():
                        if idx is not None and idx < len(row_data):
                            value = row_data[idx]
                            if pd.notna(value):
                                try:
                                    # 정수로 변환 가능한지 확인
                                    count_value = int(value)
                                    # 상태명 매핑
                                    status_map = {
                                        'meeting_days': '회의일수',
                                        'attended': '출석',
                                        'absent': '결석',
                                        'leave': '청가',
                                        'trip': '출장',
                                        'report': '결석신고서'
                                    }
                                    statuses.append((status_map[key], count_value))
                                except (ValueError, TypeError):
                                    print(f"    - 값 변환 오류: {legislator_name_str}, {key} = {value}")
                    
                    # 데이터 생성
                    for status, count in statuses:
                        attendance_data.append({
                            "legislator_name": legislator_name_str,
                            "committee_name": str(committee_name).strip(),
                            "meeting_type": "상임위",
                            "status": status,
                            "count": count,
                        })
            
            except Exception as e:
                print(f"  - 시트 '{sheet_name}' 처리 중 오류 발생: {str(e)}")
                import traceback
                traceback.print_exc()
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