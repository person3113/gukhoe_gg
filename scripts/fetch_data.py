import sys
import os
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.bill import Bill
from app.models.committee import Committee, CommitteeHistory
from app.models.sns import LegislatorSNS

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
        
        # 위원회 현황 정보 수집
        fetch_committee_info(db)

        # 처리 의안통계 수집
        fetch_processed_bills_stats(db)

        # 위원회 정보 수집 (의원-위원회 매핑)
        fetch_committees(db)

        # 위원회 경력 정보 수집 
        fetch_committee_history(db)
        
        # 발언 횟수 수집 및 업데이트 
        fetch_speech_counts(db)

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
    위원회 멤버십 정보 수집 및 DB 저장 - 상임위원회와 상설특별위원회만 필터링
    """
    from app.models.committee import Committee, CommitteeMember
    
    # 기존 데이터 확인
    existing_count = db.query(CommitteeMember).count()
    if existing_count > 0:
        print(f"이미 {existing_count}개의 위원회 멤버십 정보가 있습니다. 스킵합니다.")
        return
    
    # API 서비스 인스턴스 생성
    api_service = ApiService()
    
    # 위원회 멤버십 정보 수집
    print("위원회 멤버십 정보 수집 시작...")
    members_data = api_service.fetch_committee_members()
    
    if not members_data:
        print("수집된 위원회 멤버십 정보가 없습니다.")
        return
    
    # 현재 DB에 있는 상임위원회와 상설특별위원회 목록 가져오기
    valid_committees = db.query(Committee).filter(
        (Committee.cmt_div_nm.like('%상임위원회%')) | 
        (Committee.cmt_div_nm.like('%상설특별위원회%'))
    ).all()
    
    # 유효한 위원회 ID와 코드 목록 생성
    valid_committee_ids = {committee.id for committee in valid_committees}
    valid_committee_codes = {committee.dept_cd for committee in valid_committees}
    
    print(f"총 {len(valid_committees)}개의 상임위원회/상설특별위원회를 찾았습니다.")
    
    # 멤버십 정보 처리 및 DB 저장
    processed_count = 0
    skipped_count = 0
    filtered_count = 0
    
    for member in members_data:
        try:
            # 위원회 코드 가져오기
            dept_cd = member.get("dept_cd")
            if not dept_cd:
                print(f"위원회 코드가 없는 항목 스킵: {member}")
                skipped_count += 1
                continue
            
            # 상임위원회/상설특별위원회가 아니면 필터링
            if dept_cd not in valid_committee_codes:
                filtered_count += 1
                continue
            
            # 위원회 정보 조회 (코드 기준)
            committee = db.query(Committee).filter(Committee.dept_cd == dept_cd).first()
            
            # 위원회 정보가 없으면 이름으로 조회 시도
            if not committee:
                dept_nm = member.get("dept_nm")
                committee = db.query(Committee).filter(Committee.dept_nm == dept_nm).first()
            
            # 위원회 정보가 없거나 유효한 위원회가 아니면 스킵
            if not committee or committee.id not in valid_committee_ids:
                filtered_count += 1
                continue
            
            # 의원 정보 조회 (mona_cd 기준)
            mona_cd = member.get("mona_cd")
            if not mona_cd:
                print(f"의원 코드가 없는 항목 스킵: {member}")
                skipped_count += 1
                continue
            
            legislator = db.query(Legislator).filter(Legislator.mona_cd == mona_cd).first()
            if not legislator:
                # 이름으로 의원 조회 시도
                hg_nm = member.get("hg_nm")
                if hg_nm:
                    legislator = db.query(Legislator).filter(Legislator.hg_nm == hg_nm).first()
            
            # 의원 정보가 없으면 스킵
            if not legislator:
                print(f"의원 정보를 찾을 수 없음: {member.get('hg_nm')} ({mona_cd})")
                skipped_count += 1
                continue
            
            # 이미 위원회 멤버십이 있는지 확인
            existing_membership = db.query(CommitteeMember).filter(
                CommitteeMember.committee_id == committee.id,
                CommitteeMember.legislator_id == legislator.id
            ).first()
            
            if not existing_membership:
                # 위원회 멤버십 정보 저장
                role = member.get("job_res_nm", "위원")  # 기본값은 '위원'
                committee_member = CommitteeMember(
                    committee_id=committee.id,
                    legislator_id=legislator.id,
                    role=role
                )
                db.add(committee_member)
                processed_count += 1
                
                # 100개마다 커밋
                if processed_count % 100 == 0:
                    db.commit()
                    print(f"{processed_count}개 처리 완료...")
        
        except Exception as e:
            print(f"멤버십 정보 처리 오류: {e}, 데이터: {member}")
            skipped_count += 1
            continue
    
    # 마지막 커밋
    db.commit()
    print(f"위원회 멤버십 정보 수집 완료: {processed_count}개 (필터링: {filtered_count}개, 스킵: {skipped_count}개)")

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

def fetch_speech_counts(db: Session):
    """
    국회회의록 빅데이터 사이트에서 의원 발언 횟수 수집 및 DB 업데이트
    
    Args:
        db: 데이터베이스 세션
    """
    from app.models.legislator import Legislator
    from app.models.speech import SpeechByMeeting
    from app.utils.speech_parser import parse_speech_count_from_nanet
    from time import sleep
    
    try:
        print("국회회의록 발언 횟수 업데이트를 시작합니다...")
        
        # 처음 3명의 의원 조회
        sample_legislators = db.query(Legislator).limit(3).all()
        
        # 샘플 의원들의 발언 수 파싱하여 기존 데이터와 비교
        all_same = True
        for legislator in sample_legislators:
            # 발언 횟수 파싱
            speech_count = parse_speech_count_from_nanet(legislator.hg_nm)
            
            # 기존 발언 횟수 데이터 찾기
            existing_record = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id
            ).first()
            
            # 기존 기록이 있고 값이 같으면 계속 진행
            if existing_record and existing_record.count == speech_count:
                print(f"{legislator.hg_nm}: 발언 수 {speech_count}회 (변경 없음)")
            else:
                all_same = False
                print(f"{legislator.hg_nm}: 발언 수 {speech_count}회 (업데이트 필요)")
        
        # 모든 샘플 의원의 데이터가 같으면 나머지 의원 스킵
        if all_same:
            print("샘플 의원들의 발언 수가 모두 동일합니다. 나머지 의원들도 변경 없을 것으로 판단하여 업데이트를 스킵합니다.")
            return
        
        # 전체 의원 조회
        legislators = db.query(Legislator).all()
        
        updated_count = 0
        
        for i, legislator in enumerate(legislators):
            try:
                # 발언 횟수 파싱
                speech_count = parse_speech_count_from_nanet(legislator.hg_nm)
                
                # 발언 횟수 저장
                existing_record = db.query(SpeechByMeeting).filter(
                    SpeechByMeeting.legislator_id == legislator.id
                ).first()
                
                if existing_record:
                    # 기존 데이터 업데이트
                    existing_record.count = speech_count
                else:
                    # 새 데이터 생성 (meeting_type은 빈 문자열로 설정하여 실질적으로 사용하지 않음)
                    new_record = SpeechByMeeting(
                        legislator_id=legislator.id,
                        meeting_type="",  # 빈 문자열로 설정
                        count=speech_count
                    )
                    db.add(new_record)
                
                updated_count += 1
                print(f"[{i+1}/{len(legislators)}] {legislator.hg_nm}: {speech_count}회")
                
                # 20명마다 커밋
                if updated_count % 20 == 0:
                    db.commit()
                    print(f"{updated_count}명 업데이트 완료, 중간 저장")
                
                # 서버 부하 방지를 위한 지연
                sleep(1)
                
            except Exception as e:
                print(f"{legislator.hg_nm} 의원 업데이트 중 오류 발생: {str(e)}")
                continue
        
        # 최종 변경사항 저장
        db.commit()
        print(f"발언 횟수 업데이트 완료: 총 {updated_count}명 업데이트됨")
        
    except Exception as e:
        print(f"발언 횟수 업데이트 중 오류 발생: {str(e)}")
        db.rollback()

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