from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class SpeechKeyword(Base):
    # 테이블명 정의
    __tablename__ = "speech_keywords"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    keyword = Column(String)  # 키워드
    count = Column(Integer)  # 발언 횟수
    
    # 관계 정의
    legislator = relationship("Legislator", back_populates="speech_keywords")

class SpeechByMeeting(Base):
    # 테이블명 정의
    __tablename__ = "speech_by_meeting"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    meeting_type = Column(String)  # 회의구분
    count = Column(Integer)  # 발언 횟수
    
    # 관계 정의
    legislator = relationship("Legislator", back_populates="speech_by_meetings")