import sys
import os
from sqlalchemy.orm import Session




# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.models.sns import LegislatorSNS

from app.models.legislator import Legislator
from app.services.api_service import ApiService
from app.utils.excel_parser import parse_attendance_excel, parse_speech_keywords_excel, parse_speech_by_meeting_excel
from app.services.data_processing import process_attendance_data, process_speech_data, process_bill_data, process_vote_data
from app.services.data_processing import process_keyword_data
from scripts.calculate_scores import calculate_speech_scores
from app.models.attendance import Attendance

def fetch_all_data():
    """
    모든 데이터 수집 함수 호출
    """
    # DB 세션 생성
    db = SessionLocal()
    try:
        print("데이터 수집을 시작합니다...")
        
        # 의원 정보 수집
        fetch_legislators(db)
        
        # 법안 정보 수집
        fetch_bills(db)
        
        # 표결 정보 수집
        fetch_votes(db)
        
        # 위원회 정보 수집
        fetch_committees(db)
        
        # 위원회 현황 정보 수집
        fetch_committee_info(db)
        
        # 처리 의안통계 수집
        fetch_processed_bills_stats(db)
        
        # 엑셀 데이터 수집
        fetch_excel_data(db)
        
        print("모든 데이터 수집이 완료되었습니다.")
    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")
    finally:
        # DB 세션 닫기
        db.close()

def fetch_legislators(db: Session):
    """
    국회의원 정보, SNS 정보, 사진 정보 수집

    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_legislators_info()로 의원 정보 수집
    # 호출: api_service.fetch_legislators_sns()로 의원 SNS 정보 수집
    # 호출: api_service.fetch_legislator_images()로 의원 사진 정보 수집
    # 국회의원코드(mona_cd)를 기준으로 사진 정보 매핑 딕셔너리 생성
    # 의원 정보에 사진 URL 추가 (이미지 없는 경우 기본 이미지 경로 설정)
    # 국회의원 및 SNS 정보 DB에 저장
    """
    # 기존 데이터 확인
    existing_data = db.query(Legislator).count()
    if existing_data > 0:
        print(f"이미 {existing_data}명의 의원 정보가 있습니다. 스킵합니다.")
        return
    
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 의원 기본 정보 수집
    legislators_info = api_service.fetch_legislators_info()
    
    # SNS 정보 수집
    sns_info = api_service.fetch_legislators_sns()
    
    # 사진 정보 수집
    image_info = api_service.fetch_legislator_images()
    
    # 사진 정보를 국회의원 코드 기준으로 매핑
    image_dict = {}
    for item in image_info:
        image_dict[item['mona_cd']] = item['profile_image_url']
    
    # 의원 정보 처리 및 DB 저장
    for info in legislators_info:
        # 기존 의원 정보 확인
        legislator = db.query(Legislator).filter(Legislator.mona_cd == info['mona_cd']).first()
        
        # 사진 URL 설정
        profile_image_url = image_dict.get(info['mona_cd'], "/static/images/legislators/default.png")
        
        if legislator:
            # 기존 의원 정보 업데이트
            for key, value in info.items():
                if hasattr(legislator, key):
                    setattr(legislator, key, value)
            legislator.profile_image_url = profile_image_url
        else:
            # 새 의원 정보 생성
            legislator = Legislator(
                mona_cd=info['mona_cd'],
                hg_nm=info['hg_nm'],
                eng_nm=info.get('eng_nm'),
                bth_date=info.get('bth_date'),
                job_res_nm=info.get('job_res_nm'),
                poly_nm=info.get('poly_nm'),
                orig_nm=info.get('orig_nm'),
                cmit_nm=info.get('cmit_nm'),
                reele_gbn_nm=info.get('reele_gbn_nm'),
                sex_gbn_nm=info.get('sex_gbn_nm'),
                tel_no=info.get('tel_no'),
                e_mail=info.get('e_mail'),
                mem_title=info.get('mem_title'),
                profile_image_url=profile_image_url
            )
            db.add(legislator)
        
        # 변경사항 저장
        db.commit()
        
        # SNS 정보 처리
        sns_item = next((item for item in sns_info if item['mona_cd'] == info['mona_cd']), None)
        if sns_item:
            # 기존 SNS 정보 확인
            sns = db.query(LegislatorSNS).filter(LegislatorSNS.legislator_id == legislator.id).first()
            
            if sns:
                # 기존 SNS 정보 업데이트
                sns.twitter_url = sns_item.get('t_url')
                sns.facebook_url = sns_item.get('f_url')
                sns.youtube_url = sns_item.get('y_url')
                sns.blog_url = sns_item.get('b_url')
            else:
                # 새 SNS 정보 생성
                sns = LegislatorSNS(
                    legislator_id=legislator.id,
                    twitter_url=sns_item.get('t_url'),
                    facebook_url=sns_item.get('f_url'),
                    youtube_url=sns_item.get('y_url'),
                    blog_url=sns_item.get('b_url')
                )
                db.add(sns)
            
            # SNS 정보 변경사항 저장
            db.commit()
    
    print(f"의원 정보 수집 완료: {len(legislators_info)}명")

def fetch_bills(db: Session):
    """
    법안 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_bills()로 법안 정보 수집
    # 호출: process_bill_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_votes(db: Session):
    """
    표결 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_vote_results()로 표결 정보 수집
    # 호출: process_vote_data()로 데이터 처리
    # DB에 저장
    pass

def fetch_committees(db: Session):
    """
    위원회 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_committee_members()로 위원회 정보 수집
    # DB에 저장
    pass

def fetch_committee_info(db: Session):
    """
    위원회 현황 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_committee_info()로 위원회 현황 정보 수집
    # 위원회 테이블에서 해당 위원회 조회 후 정보 업데이트 또는 새로 생성
    # 변경사항 커밋
    pass

def fetch_processed_bills_stats(db: Session):
    """
    처리 의안통계(위원회별) 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_processed_bills_stats()로 처리 의안통계 수집
    # 위원회 테이블에서 해당 위원회 조회 후 접수건수, 처리건수 정보 업데이트
    # 변경사항 커밋
    pass

def fetch_excel_data(db: Session):
    """
    엑셀 파일에서 데이터 수집
    """
    # 호출: excel_parser.parse_attendance_excel()로 출석 데이터 수집
    # 호출: excel_parser.parse_speech_keywords_excel()로 발언 키워드 데이터 수집
    # 호출: excel_parser.parse_speech_by_meeting_excel()로 회의별 발언 데이터 수집
    # 호출: process_attendance_data(), process_speech_data()로 데이터 처리
    # DB에 저장
    """
    엑셀 파일에서 데이터 수집
    """
    import os
    import glob
    from app.utils.excel_parser import parse_speech_by_meeting_excel
    from app.services.data_processing import process_speech_data
    
    print("엑셀 데이터 수집 시작...")

    # 1. 회의별 발언 데이터 처리 
    # 엑셀 파일 경로 설정
    speech_by_meeting_dir = "data/excel/speech/speech_by_meeting"
    
    # 폴더가 존재하는지 확인하고 없으면 생성
    if not os.path.exists(speech_by_meeting_dir):
        os.makedirs(speech_by_meeting_dir, exist_ok=True)
        print(f"폴더 생성: {speech_by_meeting_dir}")
        print("발언 데이터가 없습니다. 먼저 엑셀 파일을 넣으세요.")
        return
    
    # 회의별 발언 엑셀 파일 처리
    processed_count = 0
    speech_files = glob.glob(os.path.join(speech_by_meeting_dir, "*_speech_by_meeting.xlsx"))
    total_files = len(speech_files)
    
    print(f"총 {total_files}개의 회의별 발언 파일 발견됨")
    
    for file_path in speech_files:
        filename = os.path.basename(file_path)
        print(f"파일 처리 중 ({processed_count+1}/{total_files}): {filename}")
        
        try:
            # 회의별 발언 데이터 파싱
            speech_data = parse_speech_by_meeting_excel(file_path)
            
            # 데이터 확인
            if not speech_data:
                print(f"  - 파일에서 데이터를 찾을 수 없음: {filename}")
                continue
                
            print(f"  - {len(speech_data)}개의 회의별 발언 데이터 발견")
            
            # 데이터 처리 및 DB 저장
            process_speech_data(speech_data, db)
            processed_count += 1
            
        except Exception as e:
            print(f"  - 파일 처리 오류: {filename}, 오류: {str(e)}")
    
    print(f"회의별 발언 데이터 처리 완료: {processed_count}/{total_files}개 파일")

    # speech_score 계산 
    if processed_count > 0:
        print("\n발언 점수 계산 시작...")
        calculate_speech_scores(db)
        print("발언 점수 계산 완료")

    # 2. 키워드 데이터 처리
    keywords_dir = "data/excel/speech/keywords"
    
    if os.path.exists(keywords_dir):
        processed_count = 0
        keyword_files = glob.glob(os.path.join(keywords_dir, "*_speech_keywords.xlsx"))
        total_files = len(keyword_files)
        
        print(f"\n총 {total_files}개의 키워드 파일 발견됨")
        
        for file_path in keyword_files:
            filename = os.path.basename(file_path)
            print(f"파일 처리 중 ({processed_count+1}/{total_files}): {filename}")
            
            try:
                keyword_data = parse_speech_keywords_excel(file_path)
                
                if not keyword_data:
                    print(f"  - 파일에서 데이터를 찾을 수 없음: {filename}")
                    continue
                    
                print(f"  - {len(keyword_data)}개의 키워드 데이터 발견")
                process_keyword_data(keyword_data, db)
                processed_count += 1
                
            except Exception as e:
                print(f"  - 파일 처리 오류: {filename}, 오류: {str(e)}")
        
        print(f"키워드 데이터 처리 완료: {processed_count}/{total_files}개 파일")
    else:
        print(f"키워드 폴더가 없습니다: {keywords_dir}")
    

    # 3. 출석 데이터 처리
    print("\n=== 출석 데이터 수집 ===")
    attendance_plenary_dir = "data/excel/attendance/plenary"
    attendance_standing_dir = "data/excel/attendance/standing_committee"
    
    # 폴더 존재 확인 및 생성
    for dir_path in [attendance_plenary_dir, attendance_standing_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"폴더 생성: {dir_path}")
    
    # 본회의와 상임위 파일 목록 가져오기
    plenary_files = glob.glob(os.path.join(attendance_plenary_dir, "*.xlsx"))
    standing_files = glob.glob(os.path.join(attendance_standing_dir, "*.xlsx"))
    
    # 임시 파일 필터링 (파일명에 ~$가 포함된 경우)
    plenary_files = [f for f in plenary_files if '~$' not in os.path.basename(f)]
    standing_files = [f for f in standing_files if '~$' not in os.path.basename(f)]
    
    print(f"본회의 출석 파일: {len(plenary_files)}개")
    print(f"상임위 출석 파일: {len(standing_files)}개")
    
    # 모든 출석 데이터 수집
    all_attendance_data = []
    processed_count = 0
    
    # 본회의 파일 처리
    for file_path in plenary_files:
        filename = os.path.basename(file_path)
        print(f"파일 처리 중 ({processed_count+1}/{len(plenary_files) + len(standing_files)}): {filename}")
        
        try:
            attendance_data = parse_attendance_excel(file_path)
            if attendance_data:
                all_attendance_data.extend(attendance_data)
                processed_count += 1
                print(f"  - {len(attendance_data)}개의 출석 데이터 추출")
        except Exception as e:
            print(f"  - 파일 처리 오류: {filename}, 오류: {str(e)}")
    
    # 상임위 파일 처리
    for file_path in standing_files:
        filename = os.path.basename(file_path)
        print(f"파일 처리 중 ({processed_count+1}/{len(plenary_files) + len(standing_files)}): {filename}")
        
        try:
            attendance_data = parse_attendance_excel(file_path)
            if attendance_data:
                all_attendance_data.extend(attendance_data)
                processed_count += 1
                print(f"  - {len(attendance_data)}개의 출석 데이터 추출")
        except Exception as e:
            print(f"  - 파일 처리 오류: {filename}, 오류: {str(e)}")
    
    # 출석 데이터 처리
    if all_attendance_data:
        print(f"\n총 {len(all_attendance_data)}개의 출석 데이터 처리 중...")
        
        # 기존 출석 데이터 모두 초기화
        deleted_count = db.query(Attendance).delete()
        db.commit()
        print(f"기존 출석 데이터 {deleted_count}개 삭제됨")
        
        # 모든 출석 데이터 한 번에 처리
        process_attendance_data(all_attendance_data, db)
    else:
        print("처리할 출석 데이터가 없습니다.")
    
    print(f"출석 데이터 처리 완료: {processed_count}개 파일")
    print("\n엑셀 데이터 수집 완료")

if __name__ == "__main__":
    fetch_all_data()