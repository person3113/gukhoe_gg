from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Bill(Base):
    # 테이블명 정의
    __tablename__ = "bills"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(String)  # 의안ID (BILL_ID)
    bill_no = Column(String, unique=True, index=True)  # 의안번호
    bill_name = Column(String)  # 법률안명
    propose_dt = Column(String)  # 제안일
    detail_link = Column(String)  # 상세페이지 링크
    proposer = Column(String)  # 제안자
    main_proposer_id = Column(Integer, ForeignKey("legislators.id"), index=True)  # 대표발의자 ID
    committee = Column(String)  # 소관위원회
    proc_result = Column(String)  # 본회의심의결과
    law_title = Column(String)  # 법률명
    member_list_url = Column(String)  # 공동발의자 목록 URL (추가된 필드)
    
    # 관계 정의 - 단방향 관계로 유지할 것들만 남기고 나머지 제거
    co_proposers = relationship("BillCoProposer", back_populates=None)
    votes = relationship("Vote", back_populates=None)

class BillCoProposer(Base):
    # 테이블명 정의
    __tablename__ = "bill_co_proposers"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    is_representative = Column(Boolean, default=False)  # 대표발의자 여부
    
    # 관계 정의 - 단방향으로 변경하기 위해 제거
    # bill = relationship("Bill", back_populates="co_proposers")
    # legislator = relationship("Legislator", back_populates="bill_co_proposals")