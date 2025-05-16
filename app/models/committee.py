from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Committee(Base):
    # 테이블명 정의
    __tablename__ = "committees"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    dept_cd = Column(String, unique=True, index=True)  # 위원회 코드
    dept_nm = Column(String, unique=True, index=True)  # 위원회명
    cmt_div_nm = Column(String)  # 위원회 구분 추가
    avg_score = Column(Float)  # 평균 점수
    rcp_cnt = Column(Integer)  # 접수건수
    proc_cnt = Column(Integer)  # 처리건수
    curr_cnt = Column(Integer)  # 현원
    limit_cnt = Column(Integer)  # 위원정수
    committee_chair = Column(String)  # 위원장
    
    # 관계 정의 - 단방향 관계로 유지
    members = relationship("CommitteeMember", back_populates=None)
    
class CommitteeMember(Base):
    # 테이블명 정의
    __tablename__ = "committee_members"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    role = Column(String)  # 역할 (위원장, 간사, 위원 등)
    
    # 관계 정의 - 단방향으로 변경하기 위해 제거
    # committee = relationship("Committee", back_populates="members")
    # legislator = relationship("Legislator", back_populates="committee_memberships")

class CommitteeHistory(Base):
    # 테이블명 정의
    __tablename__ = "committee_history"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    frto_date = Column(String)  # 활동기간
    profile_sj = Column(String)  # 위원회 경력
    
    # 관계 정의 - 단방향으로 변경하기 위해 제거
    # legislator = relationship("Legislator", back_populates="committee_history")