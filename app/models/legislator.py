from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Legislator(Base):
    # 테이블명 정의
    __tablename__ = "legislators"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    mona_cd = Column(String, unique=True, index=True)  # 국회의원 코드
    hg_nm = Column(String)  # 이름
    eng_nm = Column(String)  # 영문명
    bth_date = Column(String)  # 생년월일
    job_res_nm = Column(String)  # 직책명
    poly_nm = Column(String)  # 정당명
    orig_nm = Column(String)  # 선거구
    cmit_nm = Column(String)  # 대표 위원회
    reele_gbn_nm = Column(String)  # 초선/재선 구분
    sex_gbn_nm = Column(String)  # 성별
    tel_no = Column(String)  # 전화번호
    e_mail = Column(String)  # 이메일
    mem_title = Column(String)  # 약력
    profile_image_url = Column(String)  # 프로필 이미지 URL
    
    # 스코어 관련 컬럼 정의
    tier = Column(String)  # 티어 (Challenger, Master, Diamond 등)
    overall_rank = Column(Integer)  # 종합 순위
    participation_score = Column(Float)  # 참여 점수
    legislation_score = Column(Float)  # 입법활동 점수
    speech_score = Column(Float)  # 의정발언 점수
    voting_score = Column(Float)  # 표결 책임성 점수
    cooperation_score = Column(Float)  # 협치/초당적 활동 점수
    overall_score = Column(Float)  # 종합 점수
    asset = Column(BigInteger)  # 재산
    
    # 관계 정의
    sns = relationship("LegislatorSNS", back_populates="legislator", uselist=False)
    committee_memberships = relationship("CommitteeMember", back_populates="legislator")
    committee_history = relationship("CommitteeHistory", back_populates="legislator")
    bills_proposed = relationship("Bill", back_populates="main_proposer", foreign_keys="[Bill.main_proposer_id]")
    bill_co_proposals = relationship("BillCoProposer", back_populates="legislator")
    vote_results = relationship("VoteResult", back_populates="legislator")
    attendances = relationship("Attendance", back_populates="legislator")
    speech_keywords = relationship("SpeechKeyword", back_populates="legislator")
    speech_by_meetings = relationship("SpeechByMeeting", back_populates="legislator")