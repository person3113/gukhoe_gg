import pandas as pd
import os
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.assetdetailed import AssetDetailed


def parse_attendance_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    출석 현황 엑셀 파일을 파싱 (본회의 또는 상임위)
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    try:
        # 임시 파일 확인 (파일명에 ~$가 포함된 경우)
        filename = os.path.basename(file_path)
        if '~$' in filename:
            print(f"임시 파일을 건너뜁니다: {filename}")
            return []
        
        # 파일 경로 정규화 및 디렉토리 부분으로 분리
        normalized_path_parts = os.path.normpath(file_path).split(os.path.sep)
        filename = filename.lower()
        
        # 경로에 'plenary'가 포함되어 있거나 파일명에 'plenary'가 포함된 경우
        if 'plenary' in normalized_path_parts or 'plenary' in filename:
            print(f"본회의 출석 파일로 인식됨: {filename}")
            return parse_plenary_attendance_excel(file_path)
        
        # 경로에 'standing_committee'가 포함되어 있거나 파일명에 'standing'이 포함된 경우
        elif 'standing_committee' in normalized_path_parts or 'standing' in filename:
            print(f"상임위 출석 파일로 인식됨: {filename}")
            return parse_standing_committee_attendance_excel(file_path)
        
        # 한글 파일명 구분
        elif '본회의' in filename:
            print(f"본회의 출석 파일로 인식됨(한글명): {filename}")
            return parse_plenary_attendance_excel(file_path)
        elif '상임위' in filename:
            print(f"상임위 출석 파일로 인식됨(한글명): {filename}")
            return parse_standing_committee_attendance_excel(file_path)
        
        # 시트 구조로 판단 시도
        else:
            try:
                # 엑셀 시트 확인
                xls = pd.ExcelFile(file_path)
                sheets = xls.sheet_names
                
                if '22대' in sheets:
                    print(f"시트 기반으로 본회의 출석 파일로 인식됨: {filename}")
                    return parse_plenary_attendance_excel(file_path)
                else:
                    print(f"기타 출석 파일은 상임위로 처리: {filename}")
                    return parse_standing_committee_attendance_excel(file_path)
            except:
                # 마지막 대안으로 상임위로 처리
                print(f"판단 불가능한 파일은 상임위로 처리: {filename}")
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
    상임위 출석 현황 엑셀 파일을 파싱 (단순화된 버전)
    
    Args:
        file_path: 엑셀 파일 경로
    
    Returns:
        List[Dict[str, Any]]: 출석 데이터 리스트
    """
    try:
        # 엑셀 파일 로드
        df = pd.read_excel(file_path)
        
        print(f"상임위 출석 엑셀 데이터 형태: {df.shape}")
        print(f"컬럼명: {df.columns.tolist()}")
        
        # 의원별 상태별 카운트를 저장할 딕셔너리
        legislator_counts = {}
        
        # 각 행 처리
        for _, row in df.iterrows():
            # 의원명 확인
            legislator_name = row['의원명']
            if pd.isna(legislator_name) or not legislator_name:
                continue
            
            # 문자열로 변환 및 공백 제거
            legislator_name = str(legislator_name).strip()
            
            # 의원별 상태별 카운트 초기화
            if legislator_name not in legislator_counts:
                legislator_counts[legislator_name] = {
                    "회의일수": 0,
                    "출석": 0,
                    "결석": 0,
                    "청가": 0,
                    "출장": 0,
                    "결석신고서": 0
                }
            
            # 각 상태별 값 추출 및 합산
            for status in ["회의일수", "출석", "결석", "청가", "출장", "결석신고서"]:
                if status in row:
                    value = row[status]
                    if not pd.isna(value):
                        try:
                            # 문자열이나 숫자를 정수로 변환 시도
                            count = int(value)
                            legislator_counts[legislator_name][status] += count
                        except (ValueError, TypeError):
                            # 변환 불가능한 경우 경고 출력
                            print(f"경고: '{legislator_name}' 의원의 '{status}' 값 '{value}'를 정수로 변환할 수 없습니다.")
        
        # 결과 리스트 생성
        attendance_data = []
        
        # 합산된 의원별 데이터를 결과 형식으로 변환
        for legislator_name, status_counts in legislator_counts.items():
            for status, count in status_counts.items():
                attendance_data.append({
                    "legislator_name": legislator_name,
                    "meeting_type": "상임위",
                    "status": status,
                    "count": count
                })
        
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
    

def parse_asset_excel(file_path: str, db: Session) -> int:
    """
    재산 엑셀 파일을 파싱하여 AssetDetailed 모델로 DB에 저장
    
    Args:
        file_path: 엑셀 파일 경로
        db: 데이터베이스 세션
    
    Returns:
        int: 처리된 레코드 수
    """
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        
        print(f"엑셀 파일 형태: {df.shape}")
        print(f"컬럼명: {df.columns.tolist()}")
        
        # 컬럼명 출력 (디버깅용)
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        
        # 샘플 데이터 출력 (디버깅용)
        print("\n첫 번째 행의 데이터:")
        first_row = df.iloc[0]
        for col in df.columns:
            print(f"{col}: {first_row.get(col, 'N/A')}")
        
        # 연월 정보 설정 (파일에서 직접 가져옴)
        year_month = ""
        if '연월' in df.columns and not pd.isna(df['연월'].iloc[0]):
            year_month = str(df['연월'].iloc[0])
        
        # 처리된 레코드 수
        processed_count = 0
        
        # 각 행 처리
        for idx, row in df.iterrows():
            try:
                # 'NO'가 없는 행 건너뛰기 (헤더 또는 빈 행)
                if 'NO' not in row or pd.isna(row['NO']):
                    continue
                
                # 숫자 컬럼 안전하게 변환
                asset_previous = _safe_int_conversion(row.get('종전가액', 0))
                asset_increase = _safe_int_conversion(row.get('증가액', 0))
                asset_increase_real = _safe_int_conversion(row.get('증가액실거래가격', None))
                
                # 파일에 따라 '감소액' 또는 '감 소액'으로 컬럼명이 다를 수 있음
                decrease_col = '감소액' if '감소액' in df.columns else '감 소액'
                asset_decrease = _safe_int_conversion(row.get(decrease_col, 0))
                
                asset_decrease_real = _safe_int_conversion(row.get('감소액실거래가격', None))
                asset_current = _safe_int_conversion(row.get('현재가액', 0))
                
                # 소재지 데이터 처리 - '소재지 면적 등 권리의 명세' 컬럼에서 추출
                location = ""
                if '소재지 면적 등 권리의 명세' in df.columns:
                    location_val = row.get('소재지 면적 등 권리의 명세')
                    if pd.notna(location_val):
                        location = str(location_val).strip()
                        # 디버깅용 출력
                        print(f"행 {idx}: 소재지 면적 등 권리의 명세 = '{location}'")
                
                # AssetDetailed 모델에 매핑
                asset_detail = AssetDetailed(
                    report_year_month=year_month,
                    row_no=int(row['NO']),
                    mona_code=row.get('monaCode', ''),
                    role_group=row.get('구분', ''),
                    affiliation=row.get('소속', ''),
                    position=row.get('직위', ''),
                    name=row.get('이름', ''),
                    asset_category=row.get('재산구분', ''),
                    relation_to_self=row.get('본인과의 관계', ''),
                    asset_type=row.get('재산의종류', ''),
                    location=location,  # '소재지 면적 등 권리의 명세' 컬럼 값 사용
                    area_sqm="",  # 통합 컬럼을 사용하므로 빈 문자열
                    rights_detail="",  # 통합 컬럼을 사용하므로 빈 문자열
                    asset_previous=asset_previous,
                    asset_increase=asset_increase,
                    asset_increase_real=asset_increase_real,
                    asset_decrease=asset_decrease,
                    asset_decrease_real=asset_decrease_real,
                    asset_current=asset_current,
                    reason_for_change=row.get('변동사유', '')
                )
                
                db.add(asset_detail)
                processed_count += 1
                
                # 20개마다 커밋 및 로그 출력
                if processed_count % 20 == 0:
                    db.commit()
                    print(f"{processed_count}개 처리 완료...")
                
            except Exception as e:
                print(f"행 {idx} 처리 중 오류 발생: {str(e)}")
                continue
        
        # 마지막 커밋
        db.commit()
        print(f"재산 상세 데이터 처리 완료: {processed_count}개")
        
        return processed_count
        
    except Exception as e:
        db.rollback()
        print(f"재산 엑셀 파일 파싱 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def _safe_int_conversion(value, default=None):
    """천원 단위 금액을 안전하게 정수로 변환"""
    if pd.isna(value) or value == '':
        return default
    
    try:
        # 쉼표 제거 후 정수 변환
        if isinstance(value, str):
            value = value.replace(',', '')
        return int(float(value))
    except (ValueError, TypeError):
        print(f"숫자 변환 실패: {value}, 기본값 {default} 사용")
        return default