import sys
import os
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.bill import Bill
from app.models.committee import Committee, CommitteeHistory
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
        
        # 위원회 현황 정보 수집
        fetch_committee_info(db)

        # 처리 의안통계 수집
        fetch_processed_bills_stats(db)

        # 위원회 정보 수집 (의원-위원회 매핑)
        fetch_committees(db)

        # 위원회 경력 정보 수집 (추가)
        fetch_committee_history(db)
        
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
    
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_bills()로 법안 정보 수집
    # 호출: process_bill_data()로 데이터 처리
    # DB에 저장
    """
    # 기존 데이터 확인
    existing_count = db.query(Bill).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 법안 정보가 있습니다. 새로운 법안만 가져옵니다.")
    else:
        print("법안 정보가 없습니다. 모든 법안을 가져옵니다.")
    
    # ApiService 인스턴스 생성
    api_service = ApiService()
    
    # 법안 정보 수집
    print("법안 정보 수집 시작...")
    bills_data = api_service.fetch_bills()
    
    if not bills_data:
        print("수집된 새로운 법안 정보가 없습니다.")
        return
    
    # 처리된 법안 정보를 DB에 저장
    processed_bills = process_bill_data(bills_data)
    
    print(f"새로운 법안 정보 수집 완료: {len(processed_bills)}개")

def fetch_votes(db: Session):
    """
    표결 정보 수집
    """
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 표결이 있는 법안 ID 조회
    voted_bill_ids = api_service.fetch_bills_with_votes()
    
    if not voted_bill_ids:
        print("표결이 있는 법안이 없습니다.")
        return
    
    print(f"총 {len(voted_bill_ids)}개의 법안에 대한 표결 정보를 수집합니다.")
    
    # 각 법안에 대한 표결 정보 수집 및 처리
    for index, bill_id in enumerate(voted_bill_ids):
        # 진행 상황 출력
        print(f"[{index+1}/{len(voted_bill_ids)}] 법안 {bill_id}의 표결 정보 수집 중...")
        
        # 표결 정보 수집
        vote_data = api_service.fetch_vote_results(bill_id)
        
        if not vote_data:
            print(f"법안 {bill_id}의 표결 정보를 가져올 수 없습니다.")
            continue
        
        # 표결 데이터 처리
        from app.services.data_processing import process_vote_data
        processed_data = process_vote_data(vote_data, db)
        
        if not processed_data:
            print(f"법안 {bill_id}의 표결 데이터 처리에 실패했습니다.")
            continue
        
        print(f"법안 {bill_id}의 표결 정보 처리 완료: {processed_data['processed_results']}/{processed_data['total_results']} 결과 처리됨")

def fetch_committee_info(db: Session):
    """
    위원회 현황 정보 수집 - 상임위원회와 상설특별위원회만 필터링하여 저장
    """
    print("위원회 현황 정보 수집 시작...")
    
    # 기존 데이터 확인
    existing_count = db.query(Committee).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 위원회 정보가 있습니다. 업데이트를 진행합니다.")
    
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 위원회 현황 정보 수집
    committee_data = api_service.fetch_committee_info()
    
    if not committee_data:
        print("수집된 위원회 정보가 없습니다.")
        return

    # 위원회 정보 처리 및 DB 저장
    processed_count = 0
    skipped_count = 0
    updated_count = 0
    filtered_count = 0
    duplicate_names = set()  # 중복된 위원회 이름 추적용
    
    for data in committee_data:
        try:
            # 위원회 구분 확인 - 상임위원회 또는 상설특별위원회만 처리
            cmt_div_nm = data.get("cmt_div_nm", "")
            
            # 상임위원회 또는 상설특별위원회가 아닌 경우 스킵
            if "상임위원회" not in cmt_div_nm and "상설특별위원회" not in cmt_div_nm:
                filtered_count += 1
                continue
                
            # 위원회 코드 확인 - 없는 경우 스킵
            hr_dept_cd = data.get("hr_dept_cd")
            committee_name = data.get("committee_name")
            
            if not hr_dept_cd:
                print(f"위원회 코드가 없는 항목 스킵: {committee_name}")
                skipped_count += 1
                continue
                
            if not committee_name:
                print(f"위원회 이름이 없는 항목 스킵: 코드 {hr_dept_cd}")
                skipped_count += 1
                continue
            
            # 이미 처리한 위원회 이름인지 확인 (중복 검출)
            if committee_name in duplicate_names:
                # 이름을 고유하게 만들기 위해 코드를 추가
                original_name = committee_name
                committee_name = f"{committee_name}_{hr_dept_cd}"
                print(f"중복된 위원회 이름 수정: '{original_name}' -> '{committee_name}'")
            else:
                duplicate_names.add(committee_name)
            
            # 위원정수와 현원을 정수로 변환
            limit_cnt = int(data.get("limit_cnt", "0")) if data.get("limit_cnt") and data.get("limit_cnt").isdigit() else 0
            curr_cnt = int(data.get("curr_cnt", "0")) if data.get("curr_cnt") and data.get("curr_cnt").isdigit() else 0
            
            # 먼저 위원회 코드로 조회
            committee = db.query(Committee).filter(Committee.dept_cd == hr_dept_cd).first()
            
            # 코드로 찾지 못했다면 이름으로 조회
            if not committee:
                committee = db.query(Committee).filter(Committee.dept_nm == committee_name).first()
            
            if committee:
                # 기존 위원회 정보 업데이트
                committee.dept_cd = hr_dept_cd  # 코드 업데이트
                committee.dept_nm = committee_name
                committee.cmt_div_nm = cmt_div_nm
                committee.committee_chair = data.get("hg_nm", "")
                committee.limit_cnt = limit_cnt
                committee.curr_cnt = curr_cnt
                # 다른 필드들은 그대로 유지
                updated_count += 1
            else:
                # 새 위원회 정보 생성
                committee = Committee(
                    dept_cd=hr_dept_cd,
                    dept_nm=committee_name,
                    cmt_div_nm=cmt_div_nm,
                    committee_chair=data.get("hg_nm", ""),
                    limit_cnt=limit_cnt,
                    curr_cnt=curr_cnt,
                    avg_score=0.0,  # 초기값 설정
                    rcp_cnt=0,      # 초기값 설정
                    proc_cnt=0      # 초기값 설정
                )
                db.add(committee)
            
            processed_count += 1
            
            # 10개마다 커밋
            if processed_count % 10 == 0:
                db.commit()
                print(f"{processed_count}개 처리 완료...")
        
        except Exception as e:
            print(f"위원회 정보 처리 오류: {e}, 데이터: {data}")
            skipped_count += 1
            continue
    
    # 마지막 커밋
    db.commit()
    print(f"위원회 현황 정보 수집 완료: 총 {processed_count}개 (업데이트: {updated_count}개, 필터링: {filtered_count}개, 스킵: {skipped_count}개)")

def fetch_processed_bills_stats(db: Session):
    """
    처리 의안통계(위원회별) 수집
    """
    print("처리 의안통계(위원회별) 수집 시작...")
    
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 위원회별 처리 의안통계 수집
    stats_data = api_service.fetch_processed_bills_stats()
    
    if not stats_data:
        print("수집된 처리 의안통계가 없습니다.")
        return
    
    # 위원회별 통계 정보 업데이트
    updated_count = 0
    not_found_count = 0
    
    for stat in stats_data:
        # 위원회명 추출
        cmit_nm = stat.get("cmit_nm")
        if not cmit_nm:
            continue
        
        # 접수건수, 처리건수 추출 (문자열에서 정수로 변환)
        try:
            rcp_cnt = int(stat.get("rcp_cnt", "0"))
            proc_cnt = int(stat.get("proc_cnt", "0"))
        except ValueError:
            print(f"숫자 변환 오류: 위원회 {cmit_nm}의 통계값이 올바르지 않습니다.")
            continue
        
        # 해당 위원회 조회 (이름 기준)
        committee = db.query(Committee).filter(Committee.dept_nm == cmit_nm).first()
        
        if committee:
            # 위원회 정보 업데이트
            committee.rcp_cnt = rcp_cnt
            committee.proc_cnt = proc_cnt
            updated_count += 1
            
            # 10개마다 커밋
            if updated_count % 10 == 0:
                db.commit()
                print(f"{updated_count}개 위원회 통계 업데이트 완료...")
        else:
            print(f"위원회를 찾을 수 없음: {cmit_nm}")
            not_found_count += 1
    
    # 마지막 커밋
    db.commit()
    
    print(f"처리 의안통계 업데이트 완료: 총 {updated_count}개 위원회 (찾지 못한 위원회: {not_found_count}개)")

def fetch_committees(db: Session):
    """
    위원회 정보 수집
    """
    # ApiService 인스턴스 생성
    # 호출: api_service.fetch_committee_members()로 위원회 정보 수집
    # DB에 저장
    pass

def fetch_committee_history(db: Session):
    """
    국회의원 위원회 경력 정보 수집
    """
    # 기존 데이터 확인
    existing_count = db.query(CommitteeHistory).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 위원회 경력 정보가 있습니다. 스킵합니다.")
        return
    
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 위원회 경력 정보 수집
    print("위원회 경력 정보 수집 시작...")
    history_data = api_service.fetch_committee_history()
    
    if not history_data:
        print("수집된 위원회 경력 정보가 없습니다.")
        return
    
    # 위원회 경력 정보 처리 및 DB 저장
    processed_count = 0
    for history in history_data:
        # 의원 정보 조회
        legislator = db.query(Legislator).filter(Legislator.mona_cd == history["mona_cd"]).first()
        if not legislator:
            print(f"의원 정보를 찾을 수 없음: {history['hg_nm']} ({history['mona_cd']})")
            continue
        
        # 위원회 경력 정보 저장
        committee_history = CommitteeHistory(
            legislator_id=legislator.id,
            frto_date=history["frto_date"],
            profile_sj=history["profile_sj"]
        )
        db.add(committee_history)
        processed_count += 1
        
        # 100개마다 커밋
        if processed_count % 100 == 0:
            db.commit()
            print(f"{processed_count}개 처리 완료...")
    
    # 마지막 커밋
    db.commit()
    print(f"위원회 경력 정보 수집 완료: {processed_count}개")

def fetch_excel_data(db: Session):
    """
    엑셀 파일에서 데이터 수집
    """
    # 호출: excel_parser.parse_attendance_excel()로 출석 데이터 수집
    # 호출: excel_parser.parse_speech_keywords_excel()로 발언 키워드 데이터 수집
    # 호출: excel_parser.parse_speech_by_meeting_excel()로 회의별 발언 데이터 수집
    # 호출: process_attendance_data(), process_speech_data()로 데이터 처리
    # DB에 저장
    pass

if __name__ == "__main__":
    fetch_all_data()