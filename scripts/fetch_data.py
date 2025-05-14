import sys
import os
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechByMeeting, SpeechKeyword

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.legislator import Legislator
from app.services.api_service import ApiService
from app.utils.excel_parser import parse_attendance_excel, parse_speech_keywords_excel, parse_speech_by_meeting_excel
from app.services.data_processing import process_attendance_data, process_speech_data, process_bill_data, process_vote_data

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
    from app.db.database import SessionLocal
    from app.models.legislator import Legislator
    from app.models.speech import SpeechByMeeting, SpeechKeyword
    from app.models.attendance import Attendance
    from app.utils.excel_parser import parse_attendance_excel, parse_speech_keywords_excel, parse_speech_by_meeting_excel
    from app.services.data_processing import process_attendance_data, process_speech_data
    
    
    # db가 제공되지 않으면 새 세션 생성
    if db is None:
        db = SessionLocal()
    
    try:
        print("엑셀 파일에서 데이터 수집 중...")
        
        # 출석 데이터 수집
        # (기존 코드 유지)
        
        # 발언 키워드 데이터 수집
        # (기존 코드 유지)
        
        # 회의별 발언 데이터 수집 - 다양한 파일명 패턴 처리
        speech_data = []
        excel_dir = "data/excel"
        
        # 디렉토리 내 모든 파일 검사
        if os.path.exists(excel_dir):
            for filename in os.listdir(excel_dir):
                # 회의 구분별 발언 회의록 수 패턴 확인
                if "회의" in filename and "구분별" in filename and "발언" in filename and filename.endswith((".xlsx", ".xls")):
                    file_path = os.path.join(excel_dir, filename)
                    print(f"회의별 발언 파일 발견: {filename}")
                    
                    # 파일 파싱
                    file_speech_data = parse_speech_by_meeting_excel(file_path)
                    if file_speech_data:
                        speech_data.extend(file_speech_data)
                        print(f"파일 {filename}에서 {len(file_speech_data)}개 데이터 추출")
                    else:
                        print(f"파일 {filename}에서 데이터를 추출할 수 없습니다.")
        else:
            print(f"엑셀 디렉토리를 찾을 수 없습니다: {excel_dir}")
        
        # 회의별 발언 데이터 처리 및 저장
        if speech_data:
            # 데이터 처리 - process_speech_data 함수 확인
            try:
                # 먼저 process_speech_data 함수가 'type' 매개변수를 받는지 확인
                import inspect
                speech_process_sig = inspect.signature(process_speech_data)
                has_type_param = 'type' in speech_process_sig.parameters
                
                # 해당 함수의 매개변수에 따라 호출
                if has_type_param:
                    speech_processed = process_speech_data(speech_data, type="by_meeting")
                else:
                    speech_processed = process_speech_data(speech_data)
            except Exception as e:
                print(f"데이터 처리 중 오류 발생, 원본 데이터 사용: {str(e)}")
                speech_processed = speech_data
            
            # 의원명과 ID 매핑 가져오기
            legislator_map = {}
            legislators = db.query(Legislator.id, Legislator.hg_nm).all()
            for leg_id, leg_name in legislators:
                legislator_map[leg_name] = leg_id
            
            # DB에 저장
            saved_count = 0
            for speech_item in speech_processed:
                legislator_name = speech_item.get("legislator_name")
                legislator_id = legislator_map.get(legislator_name)
                
                if legislator_id:
                    # 기존 데이터 확인
                    existing = db.query(SpeechByMeeting).filter(
                        SpeechByMeeting.legislator_id == legislator_id,
                        SpeechByMeeting.meeting_type == speech_item["meeting_type"]
                    ).first()
                    
                    if existing:
                        # 기존 데이터 업데이트
                        existing.count = speech_item["count"]
                    else:
                        # 새 데이터 추가
                        db.add(SpeechByMeeting(
                            legislator_id=legislator_id,
                            meeting_type=speech_item["meeting_type"],
                            count=speech_item["count"]
                        ))
                    saved_count += 1
                else:
                    print(f"의원 '{legislator_name}'의 ID를 찾을 수 없습니다.")
            
            db.commit()
            print(f"회의별 발언 데이터 {saved_count}개 DB 저장 완료 (총 {len(speech_processed)}개 중)")
        else:
            print("저장할 회의별 발언 데이터가 없습니다.")
    
    except Exception as e:
        print(f"엑셀 데이터 수집 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        # 외부에서 제공된 DB 세션이 아닌 경우에만 닫음
        if db is not None and db != SessionLocal():
            db.close()

if __name__ == "__main__":
    fetch_all_data()