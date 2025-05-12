import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeMember, CommitteeHistory
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult
from app.models.attendance import Attendance
from app.models.speech import SpeechKeyword, SpeechByMeeting

# 데이터베이스 초기화
def init_db():
    Base.metadata.drop_all(bind=engine)  # 기존 테이블 삭제
    Base.metadata.create_all(bind=engine)  # 테이블 새로 생성

# 더미 데이터 생성
def create_dummy_data():
    db = SessionLocal()
    try:
        # 더미 의원 데이터 - 기존 5명 + 추가 10명 = 총 15명
        legislators = [
            # 기존 의원 5명 유지 (생년월일 조정하여 나이대 맞춤)
            {
                "mona_cd": "MP001",
                "hg_nm": "홍길동",
                "eng_nm": "Hong Gil Dong",
                "bth_date": "1970-01-01",  # 55세, 50대
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "서울시 강남구",
                "cmit_nm": "법제사법위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1234-5678",
                "e_mail": "hong@assembly.go.kr",
                "mem_title": "前 검사",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Challenger",
                "overall_rank": 1,
                "participation_score": 95.0,
                "legislation_score": 92.0,
                "speech_score": 88.0,
                "voting_score": 99.0,
                "cooperation_score": 85.0,
                "overall_score": 92.0,
                "asset": 500000000  # 5억
            },
            {
                "mona_cd": "MP002",
                "hg_nm": "김하늘",
                "eng_nm": "Kim Ha Neul",
                "bth_date": "1975-05-15",  # 50세, 50대
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "부산시 해운대구",
                "cmit_nm": "국토교통위원회",
                "reele_gbn_nm": "재선",
                "sex_gbn_nm": "여",
                "tel_no": "02-2345-6789",
                "e_mail": "kim@assembly.go.kr",
                "mem_title": "前 교수",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Master",
                "overall_rank": 2,
                "participation_score": 92.0,
                "legislation_score": 87.0,
                "speech_score": 91.0,
                "voting_score": 94.0,
                "cooperation_score": 89.0,
                "overall_score": 90.6,
                "asset": 350000000  # 3.5억
            },
            {
                "mona_cd": "MP003",
                "hg_nm": "이영수",
                "eng_nm": "Lee Young Soo",
                "bth_date": "1968-11-23",  # 57세, 50대
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경기도 수원시",
                "cmit_nm": "보건복지위원회",
                "reele_gbn_nm": "3선",
                "sex_gbn_nm": "남",
                "tel_no": "02-3456-7890",
                "e_mail": "lee@assembly.go.kr",
                "mem_title": "前 기업인",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 3,
                "participation_score": 89.0,
                "legislation_score": 90.0,
                "speech_score": 87.0,
                "voting_score": 92.0,
                "cooperation_score": 91.0,
                "overall_score": 89.8,
                "asset": 720000000  # 7.2억
            },
            {
                "mona_cd": "MP004",
                "hg_nm": "박지민",
                "eng_nm": "Park Ji Min",
                "bth_date": "1980-08-07",  # 45세, 40대
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "대전시 유성구",
                "cmit_nm": "과학기술정보방송통신위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "여",
                "tel_no": "02-4567-8901",
                "e_mail": "park@assembly.go.kr",
                "mem_title": "前 과학자",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 4,
                "participation_score": 91.0,
                "legislation_score": 85.0,
                "speech_score": 89.0,
                "voting_score": 86.0,
                "cooperation_score": 92.0,
                "overall_score": 88.6,
                "asset": 280000000  # 2.8억
            },
            {
                "mona_cd": "MP005",
                "hg_nm": "최준호",
                "eng_nm": "Choi Jun Ho",
                "bth_date": "1972-03-12",  # 53세, 50대
                "job_res_nm": "의원",
                "poly_nm": "정의당",
                "orig_nm": "인천시 남동구",
                "cmit_nm": "문화체육관광위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-5678-9012",
                "e_mail": "choi@assembly.go.kr",
                "mem_title": "前 시민단체 활동가",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Platinum",
                "overall_rank": 5,
                "participation_score": 85.0,
                "legislation_score": 89.0,
                "speech_score": 90.0,
                "voting_score": 84.0,
                "cooperation_score": 88.0,
                "overall_score": 87.2,
                "asset": 150000000  # 1.5억
            },
            
            # 추가 의원 10명
            # 30대 이하 - 3명
            {
                "mona_cd": "MP006",
                "hg_nm": "김영준",
                "eng_nm": "Kim Young Jun",
                "bth_date": "1995-08-15",  # 30세
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "서울시 강남구",
                "cmit_nm": "교육위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-6234-5678",
                "e_mail": "young@assembly.go.kr",
                "mem_title": "前 대학교수",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Platinum",
                "overall_rank": 25,
                "participation_score": 85.0,
                "legislation_score": 79.0,
                "speech_score": 82.0,
                "voting_score": 90.0,
                "cooperation_score": 77.0,
                "overall_score": 82.6,
                "asset": 150000000  # 1.5억
            },
            {
                "mona_cd": "MP007",
                "hg_nm": "박소연",
                "eng_nm": "Park So Yeon",
                "bth_date": "1993-04-22",  # 32세
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경기도 성남시",
                "cmit_nm": "과학기술정보방송통신위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "여",
                "tel_no": "02-7234-5678",
                "e_mail": "soyeon@assembly.go.kr",
                "mem_title": "前 IT 기업 CEO",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 15,
                "participation_score": 88.0,
                "legislation_score": 83.0,
                "speech_score": 90.0,
                "voting_score": 92.0,
                "cooperation_score": 85.0,
                "overall_score": 87.6,
                "asset": 280000000  # 2.8억
            },
            {
                "mona_cd": "MP008",
                "hg_nm": "황민우",
                "eng_nm": "Hwang Min Woo",
                "bth_date": "1990-12-03",  # 35세
                "job_res_nm": "의원",
                "poly_nm": "정의당",
                "orig_nm": "서울시 마포구",
                "cmit_nm": "환경노동위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-8234-5678",
                "e_mail": "minwoo@assembly.go.kr",
                "mem_title": "前 환경운동가",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Gold",
                "overall_rank": 30,
                "participation_score": 80.0,
                "legislation_score": 75.0,
                "speech_score": 85.0,
                "voting_score": 82.0,
                "cooperation_score": 79.0,
                "overall_score": 80.2,
                "asset": 120000000  # 1.2억
            },
            
            # 40대 - 3명 (박지민 포함 총 4명)
            {
                "mona_cd": "MP009",
                "hg_nm": "이준호",
                "eng_nm": "Lee Jun Ho",
                "bth_date": "1985-11-23",  # 40세
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "부산시 해운대구",
                "cmit_nm": "국토교통위원회",
                "reele_gbn_nm": "재선",
                "sex_gbn_nm": "남",
                "tel_no": "02-9234-5678",
                "e_mail": "junho@assembly.go.kr",
                "mem_title": "前 변호사",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Master",
                "overall_rank": 8,
                "participation_score": 92.0,
                "legislation_score": 88.0,
                "speech_score": 86.0,
                "voting_score": 94.0,
                "cooperation_score": 89.0,
                "overall_score": 89.8,
                "asset": 320000000  # 3.2억
            },
            {
                "mona_cd": "MP010",
                "hg_nm": "정민지",
                "eng_nm": "Jeong Min Ji",
                "bth_date": "1982-06-15",  # 43세
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "대구시 수성구",
                "cmit_nm": "보건복지위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "여",
                "tel_no": "02-1034-5678",
                "e_mail": "minji@assembly.go.kr",
                "mem_title": "前 의사",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 12,
                "participation_score": 90.0,
                "legislation_score": 86.0,
                "speech_score": 84.0,
                "voting_score": 89.0,
                "cooperation_score": 88.0,
                "overall_score": 87.4,
                "asset": 250000000  # 2.5억
            },
            {
                "mona_cd": "MP011",
                "hg_nm": "강동현",
                "eng_nm": "Kang Dong Hyun",
                "bth_date": "1981-01-30",  # 44세
                "job_res_nm": "의원",
                "poly_nm": "정의당",
                "orig_nm": "서울시 노원구",
                "cmit_nm": "기획재정위원회",
                "reele_gbn_nm": "재선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1134-5678",
                "e_mail": "donghyun@assembly.go.kr",
                "mem_title": "前 경제연구원",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Platinum",
                "overall_rank": 20,
                "participation_score": 84.0,
                "legislation_score": 83.0,
                "speech_score": 81.0,
                "voting_score": 88.0,
                "cooperation_score": 84.0,
                "overall_score": 84.0,
                "asset": 210000000  # 2.1억
            },
            
            # 60대 - 3명
            {
                "mona_cd": "MP012",
                "hg_nm": "박중원",
                "eng_nm": "Park Jung Won",
                "bth_date": "1965-03-25",  # 60세
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경기도 용인시",
                "cmit_nm": "외교통일위원회",
                "reele_gbn_nm": "4선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1234-1234",
                "e_mail": "jungwon@assembly.go.kr",
                "mem_title": "前 외교관",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 18,
                "participation_score": 83.0,
                "legislation_score": 85.0,
                "speech_score": 87.0,
                "voting_score": 82.0,
                "cooperation_score": 80.0,
                "overall_score": 83.4,
                "asset": 380000000  # 3.8억
            },
            {
                "mona_cd": "MP013",
                "hg_nm": "이미경",
                "eng_nm": "Lee Mi Kyung",
                "bth_date": "1962-10-05",  # 63세
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "강원도 춘천시",
                "cmit_nm": "문화체육관광위원회",
                "reele_gbn_nm": "3선",
                "sex_gbn_nm": "여",
                "tel_no": "02-1234-2345",
                "e_mail": "mikyung@assembly.go.kr",
                "mem_title": "前 문화재단 이사장",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Master",
                "overall_rank": 9,
                "participation_score": 87.0,
                "legislation_score": 89.0,
                "speech_score": 90.0,
                "voting_score": 85.0,
                "cooperation_score": 91.0,
                "overall_score": 88.4,
                "asset": 420000000  # 4.2억
            },
            {
                "mona_cd": "MP014",
                "hg_nm": "권상현",
                "eng_nm": "Kwon Sang Hyun",
                "bth_date": "1961-07-18",  # 64세
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경상북도 구미시",
                "cmit_nm": "산업통상자원중소벤처기업위원회",
                "reele_gbn_nm": "4선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1234-3456",
                "e_mail": "sanghyun@assembly.go.kr",
                "mem_title": "前 기업인",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 14,
                "participation_score": 86.0,
                "legislation_score": 84.0,
                "speech_score": 81.0,
                "voting_score": 87.0,
                "cooperation_score": 85.0,
                "overall_score": 84.6,
                "asset": 650000000  # 6.5억
            },
            
            # 70대 이상 - 2명
            {
                "mona_cd": "MP015",
                "hg_nm": "김영석",
                "eng_nm": "Kim Young Seok",
                "bth_date": "1955-07-20",  # 70세
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경상북도 포항시",
                "cmit_nm": "국방위원회",
                "reele_gbn_nm": "5선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1234-4567",
                "e_mail": "youngseok@assembly.go.kr",
                "mem_title": "前 국방장관",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Platinum",
                "overall_rank": 22,
                "participation_score": 80.0,
                "legislation_score": 82.0,
                "speech_score": 79.0,
                "voting_score": 84.0,
                "cooperation_score": 83.0,
                "overall_score": 81.6,
                "asset": 520000000  # 5.2억
            },
            {
                "mona_cd": "MP016",
                "hg_nm": "박정희",
                "eng_nm": "Park Jung Hee",
                "bth_date": "1950-12-10",  # 75세
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "전라남도 순천시",
                "cmit_nm": "농림축산식품해양수산위원회",
                "reele_gbn_nm": "6선",
                "sex_gbn_nm": "여",
                "tel_no": "02-1234-5678",
                "e_mail": "junghee@assembly.go.kr",
                "mem_title": "前 농림부 차관",
                "profile_image_url": "/static/images/legislators/default.png",
                "tier": "Diamond",
                "overall_rank": 16,
                "participation_score": 78.0,
                "legislation_score": 84.0,
                "speech_score": 76.0,
                "voting_score": 82.0,
                "cooperation_score": 88.0,
                "overall_score": 81.6,
                "asset": 580000000  # 5.8억
            }
        ]

        # Legislator 객체 생성 및 저장
        legislator_objects = []
        for leg_data in legislators:
            legislator = Legislator(**leg_data)
            db.add(legislator)
            legislator_objects.append(legislator)
        db.commit()

        # SNS 정보 추가
        sns_data = []
        for i in range(1, len(legislators) + 1):
            sns_data.append({
                "legislator_id": i,
                "twitter_url": f"https://twitter.com/member{i}",
                "facebook_url": f"https://facebook.com/member{i}",
                "youtube_url": f"https://youtube.com/member{i}",
                "blog_url": f"https://blog.naver.com/member{i}"
            })

        for sns in sns_data:
            db.add(LegislatorSNS(**sns))
        db.commit()

        # 위원회 데이터
        committees = [
            {
                "dept_nm": "법제사법위원회",
                "avg_score": 85.2,
                "rcp_cnt": 523,
                "proc_cnt": 312,
                "curr_cnt": 18,
                "limit_cnt": 20,
                "committee_chair": "홍길동"
            },
            {
                "dept_nm": "국토교통위원회",
                "avg_score": 83.7,
                "rcp_cnt": 487,
                "proc_cnt": 256,
                "curr_cnt": 16,
                "limit_cnt": 18,
                "committee_chair": "김하늘"
            },
            {
                "dept_nm": "보건복지위원회",
                "avg_score": 84.1,
                "rcp_cnt": 612,
                "proc_cnt": 289,
                "curr_cnt": 19,
                "limit_cnt": 20,
                "committee_chair": "이영수"
            },
            {
                "dept_nm": "과학기술정보방송통신위원회",
                "avg_score": 82.9,
                "rcp_cnt": 345,
                "proc_cnt": 198,
                "curr_cnt": 15,
                "limit_cnt": 16,
                "committee_chair": "박지민"
            },
            {
                "dept_nm": "문화체육관광위원회",
                "avg_score": 81.3,
                "rcp_cnt": 278,
                "proc_cnt": 152,
                "curr_cnt": 14,
                "limit_cnt": 16,
                "committee_chair": "최준호"
            },
            {
                "dept_nm": "교육위원회",
                "avg_score": 82.1,
                "rcp_cnt": 310,
                "proc_cnt": 175,
                "curr_cnt": 15,
                "limit_cnt": 16,
                "committee_chair": "김영준"
            },
            {
                "dept_nm": "환경노동위원회",
                "avg_score": 83.2,
                "rcp_cnt": 290,
                "proc_cnt": 165,
                "curr_cnt": 14,
                "limit_cnt": 15,
                "committee_chair": "김태윤"
            },
            {
                "dept_nm": "기획재정위원회",
                "avg_score": 82.5,
                "rcp_cnt": 380,
                "proc_cnt": 210,
                "curr_cnt": 16,
                "limit_cnt": 18,
                "committee_chair": "최수진"
            },
            {
                "dept_nm": "외교통일위원회",
                "avg_score": 80.8,
                "rcp_cnt": 270,
                "proc_cnt": 150,
                "curr_cnt": 14,
                "limit_cnt": 15,
                "committee_chair": "박중원"
            },
            {
                "dept_nm": "국방위원회",
                "avg_score": 81.2,
                "rcp_cnt": 240,
                "proc_cnt": 135,
                "curr_cnt": 13,
                "limit_cnt": 14,
                "committee_chair": "김영석"
            },
            {
                "dept_nm": "농림축산식품해양수산위원회",
                "avg_score": 80.5,
                "rcp_cnt": 265,
                "proc_cnt": 140,
                "curr_cnt": 15,
                "limit_cnt": 16,
                "committee_chair": "박정희"
            },
            {
                "dept_nm": "산업통상자원중소벤처기업위원회",
                "avg_score": 81.7,
                "rcp_cnt": 320,
                "proc_cnt": 185,
                "curr_cnt": 16,
                "limit_cnt": 17,
                "committee_chair": "권상현"
            }
        ]

        committee_objects = []
        for comm_data in committees:
            committee = Committee(**comm_data)
            db.add(committee)
            committee_objects.append(committee)
        db.commit()

        # 위원회 멤버십 (의원 수에 맞게 위원회 할당)
        for i, legislator in enumerate(legislator_objects):
            # 위원회 ID는 11개 위원회 중 모듈러 연산으로 할당
            committee_id = (i % len(committee_objects)) + 1
            role = "위원장" if committees[committee_id - 1]["committee_chair"] == legislator.hg_nm else "위원"
            
            member = CommitteeMember(
                committee_id=committee_id,
                legislator_id=i+1,
                role=role
            )
            db.add(member)
        db.commit()

        # 위원회 경력
        for i, legislator in enumerate(legislator_objects):
            committee_id = (i % len(committee_objects))
            
            history = CommitteeHistory(
                legislator_id=i+1,
                frto_date="2020-06-01 ~ 현재",
                profile_sj=f"제22대 {committees[committee_id]['dept_nm']}"
            )
            db.add(history)
        db.commit()

        # 법안 데이터 (의원 수에 맞게 확장)
        bills = []
        for i in range(1, len(legislators) + 1):
            bill_name = f"{legislators[i-1]['cmit_nm']} 관련 일부개정법률안"
            bills.append({
                "bill_no": f"2113{i:03d}",
                "bill_name": bill_name,
                "propose_dt": f"2025-{(i%12)+1:02d}-{(i%28)+1:02d}",
                "detail_link": f"https://open.assembly.go.kr/bill/2113{i:03d}",
                "proposer": f"{legislators[i-1]['hg_nm']}의원 등 {10+i%10}인",
                "main_proposer_id": i,
                "committee": legislators[i-1]["cmit_nm"],
                "proc_result": ["계류중", "소위심사중", "본회의 가결", "위원회 의결", "본회의 부결"][i % 5],
                "law_title": bill_name.split(" ")[0]
            })

        bill_objects = []
        for bill_data in bills:
            bill = Bill(**bill_data)
            db.add(bill)
            bill_objects.append(bill)
        db.commit()

        # 법안 공동발의자
        for i, bill in enumerate(bill_objects):
            # 각 법안마다 다른 의원을 공동발의자로 추가 (3~5명)
            co_proposer_count = 3 + (i % 3)  # 3~5명
            co_proposers = []
            
            for j in range(co_proposer_count):
                co_proposer_id = ((i + j + 1) % len(legislators)) + 1
                if co_proposer_id != bill.main_proposer_id and co_proposer_id not in co_proposers:
                    co_proposers.append(co_proposer_id)
                    db.add(BillCoProposer(
                        bill_id=bill.id,
                        legislator_id=co_proposer_id
                    ))
        db.commit()

        # 표결 및 결과 (더 많은 표결 생성)
        for i in range(1, 6):  # 5개의 표결 생성
            vote = Vote(
                vote_date=f"2025-03-{i:02d}",
                bill_id=i  # 첫 5개 법안에 대한 표결
            )
            db.add(vote)
            db.commit()
            
            # 각 의원의 표결 결과
            for j in range(1, len(legislators) + 1):
                result = ["찬성", "반대", "기권"][j % 3 if j % 2 == 0 else 0]  # 찬성 비율을 높임
                db.add(VoteResult(
                    vote_id=vote.id,
                    legislator_id=j,
                    result_vote_mod=result
                ))
        db.commit()

        # 출석 데이터
        attendance_statuses = ["출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "출석", "결석", "청가"]
        for i, legislator in enumerate(legislator_objects):
            for meeting_date in ["2025-02-15", "2025-03-01", "2025-03-15", "2025-04-01", "2025-04-15"]:
                status_idx = (i + int(meeting_date.split('-')[2])) % len(attendance_statuses)
                db.add(Attendance(
                    legislator_id=i+1,
                    committee_id=(i % len(committee_objects)) + 1,
                    meeting_date=meeting_date,
                    meeting_type=["본회의", "상임위원회"][i % 2],
                    status=attendance_statuses[status_idx]
                ))
        db.commit()

        # 회의별 발언 데이터
        meeting_types = ["본회의", "상임위원회", "특별위원회", "예산결산특별위원회", "국정감사", "국정조사", "전원위원회", "소위원회"]
        
        for i, legislator in enumerate(legislator_objects):
            # 실제 데이터의 분포를 반영한 발언 데이터 생성
            # 의원의 나이대에 따라 발언 패턴이 다르게 나타나도록 조정
            bth_year = int(legislator.bth_date.split('-')[0])
            age = 2025 - bth_year
            
            # 나이대별 발언 패턴 조정
            if age < 40:  # 30대 이하: 본회의/상임위/소위원회 발언 많음
                counts = [3, 17, 1, 0, 3, 0, 0, 9]
            elif age < 50:  # 40대: 상임위/국정감사 발언 많음
                counts = [2, 20, 0, 1, 12, 0, 0, 5]
            elif age < 60:  # 50대: 본회의/상임위/국정감사 발언 많음 (최대)
                counts = [4, 25, 2, 3, 15, 1, 1, 8]
            elif age < 70:  # 60대: 중간 정도
                counts = [3, 18, 1, 3, 10, 1, 0, 6]
            else:  # 70대 이상: 조금 적음
                counts = [2, 15, 0, 2, 8, 0, 0, 5]
            
            # 개인별 특성 반영 (점수가 높은 의원은 발언도 많이 함)
            score_factor = legislator.overall_score / 85.0  # 85점을 기준으로 비례 조정
            counts = [max(0, int(count * score_factor)) for count in counts]
            
            for j, meeting_type in enumerate(meeting_types):
                if counts[j] > 0:  # 발언 수가 0인 경우는 추가하지 않음
                    db.add(SpeechByMeeting(
                        legislator_id=i+1,
                        meeting_type=meeting_type,
                        count=counts[j]
                    ))
        db.commit()

        # 발언 키워드 데이터
        keywords_by_committee = {
            "법제사법위원회": ["법안", "사법", "법원", "변호사", "재판", "형법", "헌법", "검찰", "기소", "판결"],
            "국토교통위원회": ["주택", "교통", "도시", "개발", "SOC", "도로", "철도", "부동산", "건설", "택지"],
            "보건복지위원회": ["의료", "복지", "건강", "환자", "병원", "보험", "요양", "약제", "의약품", "질병"],
            "과학기술정보방송통신위원회": ["과학", "기술", "통신", "방송", "인터넷", "데이터", "연구", "개발", "혁신", "디지털"],
            "문화체육관광위원회": ["문화", "체육", "관광", "예술", "콘텐츠", "저작권", "공연", "여행", "스포츠", "전시"],
            "교육위원회": ["교육", "학교", "학생", "교사", "대학", "입시", "학력", "교과", "기초학력", "평가"],
            "환경노동위원회": ["환경", "노동", "근로", "고용", "임금", "기후", "오염", "탄소", "안전", "단체협약"],
            "기획재정위원회": ["예산", "세금", "재정", "경제", "물가", "금리", "금융", "세입", "세출", "국가부채"],
            "외교통일위원회": ["외교", "통일", "북한", "안보", "국제", "협력", "조약", "평화", "동맹", "제재"],
            "국방위원회": ["국방", "군사", "안보", "병력", "전력", "방위", "무기", "전투", "훈련", "병역"],
            "농림축산식품해양수산위원회": ["농업", "축산", "어업", "해양", "수산", "식량", "농산물", "식품", "수산물", "농촌"],
            "산업통상자원중소벤처기업위원회": ["산업", "통상", "무역", "중소기업", "벤처", "자원", "에너지", "수출", "제조", "창업"]
        }
        
        for i, legislator in enumerate(legislator_objects):
            committee = legislator.cmit_nm
            if committee in keywords_by_committee:
                keywords = keywords_by_committee[committee]
            else:
                # 위원회가 매핑되지 않은 경우 기본 키워드 사용
                keywords = ["국회", "정책", "법률", "예산", "민생", "개혁", "국민", "경제", "사회", "발전"]
            
            # 의원 나이대에 따른 키워드 사용 빈도 차이
            bth_year = int(legislator.bth_date.split('-')[0])
            age = 2025 - bth_year
            
            # 나이대별 키워드 빈도 패턴 조정
            if age < 40:  # 30대 이하: 중간 빈도
                base_count = 80
            elif age < 50:  # 40대: 중상 빈도
                base_count = 100
            elif age < 60:  # 50대: 최고 빈도
                base_count = 130
            elif age < 70:  # 60대: 중상 빈도
                base_count = 110
            else:  # 70대 이상: 중하 빈도
                base_count = 90
            
            # 개인별 특성 반영
            score_factor = legislator.speech_score / 85.0
            
            # 키워드별 빈도 - 지수적으로 감소
            for j, keyword in enumerate(keywords):
                # 첫 키워드가 가장 많고, 이후 지수적으로 감소
                count = int(base_count * score_factor * (0.85 ** j))
                if count > 0:
                    db.add(SpeechKeyword(
                        legislator_id=i+1,
                        keyword=keyword,
                        count=count
                    ))
        db.commit()

        print("더미 데이터 생성 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()
