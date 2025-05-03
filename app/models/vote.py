from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Vote(Base):
    # 테이블명 정의
    __tablename__ = "votes"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    vote_date = Column(String)  # 의결일자
    bill_id = Column(Integer, ForeignKey("bills.id"), index=True)
    
    # 관계 정의
    bill = relationship("Bill", back_populates="votes")
    results = relationship("VoteResult", back_populates="vote")

class VoteResult(Base):
    # 테이블명 정의
    __tablename__ = "vote_results"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    vote_id = Column(Integer, ForeignKey("votes.id"), index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    result_vote_mod = Column(String)  # 표결결과 (찬성/반대/기권)
    
    # 관계 정의
    vote = relationship("Vote", back_populates="results")
    legislator = relationship("Legislator", back_populates="vote_results")