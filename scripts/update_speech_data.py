# scripts/update_speech_data.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

# 모든 필요한 모델 임포트
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechByMeeting

def process_speech_excel_files(db: Session):
    """
    모든 엑셀 파일 처리
    """
    # 프로젝트 루트 디렉토리 찾기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # speech 디렉토리
    speech_dir = os.path.join(project_root, "data", "excel", "speech")
    
    print(f"프로젝트 루트: {project_root}")
    print(f"speech 디렉토리: {speech_dir}")
    
    if not os.path.exists(speech_dir):
        print(f"❌ speech 디렉토리가 존재하지 않습니다: {speech_dir}")
        return
    
    # speech 디렉토리 내의 하위 폴더들(의원명 폴더)을 탐색
    success_count = 0
    fail_count = 0
    total_files = 0
    
    # 의원명 폴더들 목록
    legislator_folders = [f for f in os.listdir(speech_dir) 
                         if os.path.isdir(os.path.join(speech_dir, f))]
    
    print(f"발견된 의원 폴더 수: {len(legislator_folders)}")
    print(f"의원 폴더 목록: {legislator_folders[:5]}...")  # 처음 5개만 표시
    
    for folder_name in legislator_folders:
        folder_path = os.path.join(speech_dir, folder_name)
        print(f"\n{'='*50}")
        print(f"의원 폴더 처리 중: {folder_name}")
        
        # 폴더 내의 엑셀 파일 찾기
        excel_files = [f for f in os.listdir(folder_path) 
                      if f.endswith('.xlsx') and f.startswith('통합검색_국회회의록_발언자목록_')]
        
        if not excel_files:
            print(f"⚠️ {folder_name} 폴더에 엑셀 파일이 없습니다.")
            continue
        
        for file_name in excel_files:
            file_path = os.path.join(folder_path, file_name)
            total_files += 1
            
            # 파일명에서 의원 이름 추출
            # "통합검색_국회회의록_발언자목록_강경숙+(姜景淑)_2025-05-09_전체+회의+구분별+발언+회의록+수.xlsx"
            parts = file_name.split('_')
            if len(parts) >= 5:
                name_part = parts[3]
                legislator_name = name_part.split('+')[0]
            else:
                # 폴더명을 의원명으로 사용
                legislator_name = folder_name
            
            print(f"\n파일 처리 중: {file_name}")
            print(f"의원명: {legislator_name}")
            
            if process_single_speech_file(db, file_path, legislator_name):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n{'='*50}")
    print(f"전체 처리 완료:")
    print(f"- 총 파일 수: {total_files}")
    print(f"- 성공: {success_count}")
    print(f"- 실패: {fail_count}")

def process_single_speech_file(db: Session, file_path: str, legislator_name: str) -> bool:
    """
    단일 엑셀 파일 처리
    """
    try:
        print(f"파일 처리 시작: {legislator_name}")
        
        # 헤더가 두 번째 행(인덱스 1)에 있음
        df = pd.read_excel(file_path, header=1)
        
        # 예상 컬럼명 확인
        expected_columns = ['발언자', '대수', '회의구분', '회의록수']
        actual_columns = df.columns.tolist()
        
        # 컬럼명이 다른 경우 직접 설정
        if actual_columns != expected_columns:
            df.columns = expected_columns
        
        print(f"데이터 행 수: {len(df)}")
        
        # 의원 정보 조회
        legislator = db.query(Legislator).filter(Legislator.hg_nm == legislator_name).first()
        if not legislator:
            print(f"⚠️ 경고: {legislator_name} 의원을 데이터베이스에서 찾을 수 없습니다.")
            
            # 비슷한 이름의 의원 검색
            similar = db.query(Legislator).filter(
                Legislator.hg_nm.like(f"%{legislator_name[:-1]}%")
            ).all()
            if similar:
                print(f"   비슷한 의원: {[s.hg_nm for s in similar]}")
            return False
        
        print(f"의원 ID: {legislator.id}")
        
        # 기존 데이터 삭제
        existing_count = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.legislator_id == legislator.id
        ).count()
        
        if existing_count > 0:
            db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id
            ).delete()
            print(f"기존 데이터 {existing_count}개 삭제")
        
        # 새 데이터 추가
        added_count = 0
        
        for _, row in df.iterrows():
            # 빈 값이나 'Total' 행 건너뛰기
            if pd.isna(row['회의록수']) or row['회의구분'] == 'Total':
                continue
            
            count = int(row['회의록수'])
            if count > 0:  # 발언 수가 0보다 큰 경우만 저장
                meeting_type = row['회의구분'].strip()
                speech_data = SpeechByMeeting(
                    legislator_id=legislator.id,
                    meeting_type=meeting_type,
                    count=count
                )
                db.add(speech_data)
                added_count += 1
                print(f"  - {meeting_type}: {count}회")
        
        # 변경사항 커밋
        db.commit()
        print(f"✅ {legislator_name}: {added_count}개 데이터 추가 완료")
        
        # Total 값 확인 (의정발언 점수용)
        total_row = df[df['회의구분'] == 'Total']
        if not total_row.empty:
            total_speech = int(total_row['회의록수'].iloc[0])
            print(f"총 발언 수(Total): {total_speech}회")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

def update_speech_scores(db: Session):
    """
    의정발언 점수 업데이트
    """
    print("\n의정발언 점수 업데이트 중...")
    
    # 모든 의원 조회
    legislators = db.query(Legislator).all()
    
    for legislator in legislators:
        # 해당 의원의 총 발언 수 계산
        total_speech = db.query(
            db.func.sum(SpeechByMeeting.count)
        ).filter(
            SpeechByMeeting.legislator_id == legislator.id
        ).scalar() or 0
        
        # 점수 계산 (예: 단순 비례식)
        # 실제로는 더 복잡한 계산식이 필요할 수 있음
        max_speech = 100  # 가정: 최대 발언 수
        speech_score = min(100, (total_speech / max_speech) * 100)
        
        # 의원 정보 업데이트
        legislator.speech_score = round(speech_score, 1)
        
        print(f"{legislator.hg_nm}: 총 발언 {total_speech}회 -> 점수 {speech_score:.1f}")
    
    db.commit()
    print("✅ 의정발언 점수 업데이트 완료")

def main():
    """
    메인 함수
    """
    db = SessionLocal()
    try:
        print("발언 데이터 업데이트 시작...")
        
        # 1. 엑셀 파일 처리
        process_speech_excel_files(db)
        
        # 2. 의정발언 점수 업데이트
        update_speech_scores(db)
        
        print("\n모든 처리가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 전체 프로세스 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()