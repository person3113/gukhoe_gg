import sys
import os
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.sns import LegislatorSNS

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
    from app.models.speech import SpeechByMeeting
    from app.utils.excel_parser import parse_speech_by_meeting_excel
    
    # 의원 전체 조회
    legislators = db.query(Legislator).all()
    
    # 엑셀 파일 디렉토리
    excel_dir = "data/excel/speech"
    
    print(f"엑셀 데이터 수집 시작 - 총 {len(legislators)}명의 의원")
    
    for legislator in legislators:
        # 파일명 패턴: "통합검색_국회회의록_발언자목록_{이름}+...xlsx"
        matching_files = []
        for filename in os.listdir(excel_dir):
            if filename.endswith('.xlsx') and legislator.hg_nm in filename:
                matching_files.append(filename)
        
        if not matching_files:
            print(f"의원 {legislator.hg_nm}의 엑셀 파일을 찾을 수 없습니다.")
            continue
        
        # 첫 번째 매칭 파일 사용
        file_path = os.path.join(excel_dir, matching_files[0])
        
        # 엑셀 파일 파싱
        speech_data = parse_speech_by_meeting_excel(file_path)
        
        # Total 값을 먼저 저장
        total_speech = db.query(SpeechByMeeting).filter(
            SpeechByMeeting.legislator_id == legislator.id,
            SpeechByMeeting.meeting_type == 'Total'
        ).first()
        
        if total_speech:
            total_speech.count = speech_data['total']
        else:
            new_total = SpeechByMeeting(
                legislator_id=legislator.id,
                meeting_type='Total',
                count=speech_data['total']
            )
            db.add(new_total)
        
        # 나머지 회의별 발언수 저장
        for meeting_data in speech_data['by_meeting']:
            existing = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id,
                SpeechByMeeting.meeting_type == meeting_data['meeting_type']
            ).first()
            
            if existing:
                existing.count = meeting_data['count']
            else:
                new_speech = SpeechByMeeting(
                    legislator_id=legislator.id,
                    meeting_type=meeting_data['meeting_type'],
                    count=meeting_data['count']
                )
                db.add(new_speech)
        
        print(f"의원 {legislator.hg_nm}의 발언 데이터 처리 완료")
    
    db.commit()
    print("엑셀 데이터 수집 완료!")

if __name__ == "__main__":
    fetch_all_data()