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
        # 더미 의원 데이터
        legislators = [
            {
                "mona_cd": "MP001",
                "hg_nm": "홍길동",
                "eng_nm": "Hong Gil Dong",
                "bth_date": "1970-01-01",
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "서울시 강남구",
                "cmit_nm": "법제사법위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-1234-5678",
                "e_mail": "hong@assembly.go.kr",
                "mem_title": "前 검사",
                "profile_image_url": "/static/images/legislators/default.png",  # 모두 default.png로 통일
                "tier": "Challenger",
                "overall_rank": 1,
                "participation_score": 95.0,
                "legislation_score": 92.0,
                "speech_score": 88.0,
                "voting_score": 99.0,
                "cooperation_score": 85.0,
                "overall_score": 92.0,
                "asset": 500000000
            },
            {
                "mona_cd": "MP002",
                "hg_nm": "김하늘",
                "eng_nm": "Kim Ha Neul",
                "bth_date": "1975-05-15",
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "부산시 해운대구",
                "cmit_nm": "국토교통위원회",
                "reele_gbn_nm": "재선",
                "sex_gbn_nm": "여",
                "tel_no": "02-2345-6789",
                "e_mail": "kim@assembly.go.kr",
                "mem_title": "前 교수",
                "profile_image_url": "/static/images/legislators/default.png",  # 모두 default.png로 통일
                "tier": "Master",
                "overall_rank": 2,
                "participation_score": 92.0,
                "legislation_score": 87.0,
                "speech_score": 91.0,
                "voting_score": 94.0,
                "cooperation_score": 89.0,
                "overall_score": 90.6,
                "asset": 350000000
            },
            {
                "mona_cd": "MP003",
                "hg_nm": "이영수",
                "eng_nm": "Lee Young Soo",
                "bth_date": "1968-11-23",
                "job_res_nm": "의원",
                "poly_nm": "국민의힘",
                "orig_nm": "경기도 수원시",
                "cmit_nm": "보건복지위원회",
                "reele_gbn_nm": "3선",
                "sex_gbn_nm": "남",
                "tel_no": "02-3456-7890",
                "e_mail": "lee@assembly.go.kr",
                "mem_title": "前 기업인",
                "profile_image_url": "/static/images/legislators/default.png",  # 모두 default.png로 통일
                "tier": "Diamond",
                "overall_rank": 3,
                "participation_score": 89.0,
                "legislation_score": 90.0,
                "speech_score": 87.0,
                "voting_score": 92.0,
                "cooperation_score": 91.0,
                "overall_score": 89.8,
                "asset": 720000000
            },
            {
                "mona_cd": "MP004",
                "hg_nm": "박지민",
                "eng_nm": "Park Ji Min",
                "bth_date": "1980-08-07",
                "job_res_nm": "의원",
                "poly_nm": "더불어민주당",
                "orig_nm": "대전시 유성구",
                "cmit_nm": "과학기술정보방송통신위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "여",
                "tel_no": "02-4567-8901",
                "e_mail": "park@assembly.go.kr",
                "mem_title": "前 과학자",
                "profile_image_url": "/static/images/legislators/default.png",  # 모두 default.png로 통일
                "tier": "Diamond",
                "overall_rank": 4,
                "participation_score": 91.0,
                "legislation_score": 85.0,
                "speech_score": 89.0,
                "voting_score": 86.0,
                "cooperation_score": 92.0,
                "overall_score": 88.6,
                "asset": 280000000
            },
            {
                "mona_cd": "MP005",
                "hg_nm": "최준호",
                "eng_nm": "Choi Jun Ho",
                "bth_date": "1972-03-12",
                "job_res_nm": "의원",
                "poly_nm": "정의당",
                "orig_nm": "인천시 남동구",
                "cmit_nm": "문화체육관광위원회",
                "reele_gbn_nm": "초선",
                "sex_gbn_nm": "남",
                "tel_no": "02-5678-9012",
                "e_mail": "choi@assembly.go.kr",
                "mem_title": "前 시민단체 활동가",
                "profile_image_url": "/static/images/legislators/default.png",  # 모두 default.png로 통일
                "tier": "Platinum",
                "overall_rank": 5,
                "participation_score": 85.0,
                "legislation_score": 89.0,
                "speech_score": 90.0,
                "voting_score": 84.0,
                "cooperation_score": 88.0,
                "overall_score": 87.2,
                "asset": 150000000
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
        sns_data = [
            {
                "legislator_id": 1,
                "twitter_url": "https://twitter.com/hongGD",
                "facebook_url": "https://facebook.com/hongGD",
                "youtube_url": "https://youtube.com/hongGD",
                "blog_url": "https://blog.naver.com/hongGD"
            },
            {
                "legislator_id": 2,
                "twitter_url": "https://twitter.com/kimHN",
                "facebook_url": "https://facebook.com/kimHN",
                "youtube_url": "https://youtube.com/kimHN",
                "blog_url": "https://blog.naver.com/kimHN"
            },
            {
                "legislator_id": 3,
                "twitter_url": "https://twitter.com/leeYS",
                "facebook_url": "https://facebook.com/leeYS",
                "youtube_url": "https://youtube.com/leeYS",
                "blog_url": "https://blog.naver.com/leeYS"
            },
            {
                "legislator_id": 4,
                "twitter_url": "https://twitter.com/parkJM",
                "facebook_url": "https://facebook.com/parkJM",
                "youtube_url": "https://youtube.com/parkJM",
                "blog_url": "https://blog.naver.com/parkJM"
            },
            {
                "legislator_id": 5,
                "twitter_url": "https://twitter.com/choiJH",
                "facebook_url": "https://facebook.com/choiJH",
                "youtube_url": "https://youtube.com/choiJH",
                "blog_url": "https://blog.naver.com/choiJH"
            }
        ]

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
            }
        ]

        committee_objects = []
        for comm_data in committees:
            committee = Committee(**comm_data)
            db.add(committee)
            committee_objects.append(committee)
        db.commit()

        # 위원회 멤버십
        for i, legislator in enumerate(legislator_objects):
            member = CommitteeMember(
                committee_id=i+1,
                legislator_id=i+1,
                role="위원장" if i==0 else "위원"
            )
            db.add(member)
        db.commit()

        # 위원회 경력
        for i, legislator in enumerate(legislator_objects):
            history = CommitteeHistory(
                legislator_id=i+1,
                frto_date="2020-06-01 ~ 현재",
                profile_sj=f"제22대 {committees[i]['dept_nm']}"
            )
            db.add(history)
        db.commit()

        # 법안 데이터
        bills = [
            {
                "bill_no": "2113001",
                "bill_name": "국회법 일부개정법률안",
                "propose_dt": "2025-01-15",
                "detail_link": "https://open.assembly.go.kr/bill/2113001",
                "proposer": "홍길동의원 등 15인",
                "main_proposer_id": 1,
                "committee": "법제사법위원회",
                "proc_result": "계류중",
                "law_title": "국회법"
            },
            {
                "bill_no": "2113002",
                "bill_name": "주택임대차보호법 일부개정법률안",
                "propose_dt": "2025-01-28",
                "detail_link": "https://open.assembly.go.kr/bill/2113002",
                "proposer": "김하늘의원 등 12인",
                "main_proposer_id": 2,
                "committee": "국토교통위원회",
                "proc_result": "소위심사중",
                "law_title": "주택임대차보호법"
            },
            {
                "bill_no": "2113003",
                "bill_name": "의료법 일부개정법률안",
                "propose_dt": "2025-02-05",
                "detail_link": "https://open.assembly.go.kr/bill/2113003",
                "proposer": "이영수의원 등 18인",
                "main_proposer_id": 3,
                "committee": "보건복지위원회",
                "proc_result": "본회의 가결",
                "law_title": "의료법"
            },
            {
                "bill_no": "2113004",
                "bill_name": "정보통신망법 일부개정법률안",
                "propose_dt": "2025-02-12",
                "detail_link": "https://open.assembly.go.kr/bill/2113004",
                "proposer": "박지민의원 등 10인",
                "main_proposer_id": 4,
                "committee": "과학기술정보방송통신위원회",
                "proc_result": "위원회 의결",
                "law_title": "정보통신망법"
            },
            {
                "bill_no": "2113005",
                "bill_name": "저작권법 일부개정법률안",
                "propose_dt": "2025-02-28",
                "detail_link": "https://open.assembly.go.kr/bill/2113005",
                "proposer": "최준호의원 등 9인",
                "main_proposer_id": 5,
                "committee": "문화체육관광위원회",
                "proc_result": "계류중",
                "law_title": "저작권법"
            }
        ]

        bill_objects = []
        for bill_data in bills:
            bill = Bill(**bill_data)
            db.add(bill)
            bill_objects.append(bill)
        db.commit()

        # 법안 공동발의자
        for i, bill in enumerate(bill_objects):
            # 각 법안마다 다른 의원을 공동발의자로 추가
            co_proposers = [j+1 for j in range(5) if j != i]
            for co_proposer_id in co_proposers[:3]:  # 각 법안당 3명의 공동발의자
                db.add(BillCoProposer(
                    bill_id=bill.id,
                    legislator_id=co_proposer_id
                ))
        db.commit()

        # 표결 및 결과
        vote = Vote(
            vote_date="2025-03-01",
            bill_id=3  # 의료법 표결
        )
        db.add(vote)
        db.commit()

        # 표결 결과
        vote_results = [
            {"legislator_id": 1, "result_vote_mod": "찬성"},
            {"legislator_id": 2, "result_vote_mod": "찬성"},
            {"legislator_id": 3, "result_vote_mod": "찬성"},
            {"legislator_id": 4, "result_vote_mod": "반대"},
            {"legislator_id": 5, "result_vote_mod": "기권"}
        ]

        for result in vote_results:
            db.add(VoteResult(
                vote_id=vote.id,
                **result
            ))
        db.commit()

        # 출석 데이터
        attendance_statuses = ["출석", "출석", "출석", "출석", "결석"]
        for i, legislator in enumerate(legislator_objects):
            db.add(Attendance(
                legislator_id=i+1,
                committee_id=i+1,
                meeting_date="2025-03-15",
                meeting_type="본회의",
                status=attendance_statuses[i]
            ))
        db.commit()

        # 발언 키워드 데이터
        keywords = [
            ["법안", "사법", "법원", "변호사", "재판"],
            ["주택", "교통", "도시", "개발", "SOC"],
            ["의료", "복지", "건강", "환자", "병원"],
            ["과학", "기술", "통신", "방송", "인터넷"],
            ["문화", "체육", "관광", "예술", "콘텐츠"]
        ]

        for i, legislator in enumerate(legislator_objects):
            for j, keyword in enumerate(keywords[i]):
                db.add(SpeechKeyword(
                    legislator_id=i+1,
                    keyword=keyword,
                    count=100 - j*10  # 100, 90, 80, 70, 60
                ))
        db.commit()

        # 회의별 발언 데이터
        meeting_types = ["본회의", "상임위", "소위원회", "국정감사", "국정조사"]
        for i, legislator in enumerate(legislator_objects):
            for j, meeting_type in enumerate(meeting_types):
                db.add(SpeechByMeeting(
                    legislator_id=i+1,
                    meeting_type=meeting_type,
                    count=50 - j*5  # 50, 45, 40, 35, 30
                ))
        db.commit()

        print("더미 데이터 생성 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("데이터베이스 초기화 중...")
    init_db()
    print("더미 데이터 생성 중...")
    create_dummy_data()