from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Attendance(Base):
    # 테이블명 정의
    __tablename__ = "attendance"
    
    # 기본 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True, index=True)
    meeting_date = Column(String)  # 회의일자 
    meeting_type = Column(String)  # 회의구분 (본회의/상임위)
    status = Column(String)  # 출석상태 (출석/결석/청가/출장/결석신고서)
    count = Column(Integer, default=0)  # 카운트 필드 추가
    # 관계 정의 - 단방향으로 변경하기 위해 제거
    # legislator = relationship("Legislator", back_populates="attendances")
    # committee = relationship("Committee", back_populates="attendances")