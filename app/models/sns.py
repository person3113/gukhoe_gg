from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class LegislatorSNS(Base):
    # 테이블명 정의
    __tablename__ = "legislator_sns"
    
    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    legislator_id = Column(Integer, ForeignKey("legislators.id"), index=True)
    twitter_url = Column(String)
    facebook_url = Column(String)
    youtube_url = Column(String)
    blog_url = Column(String)
    
    # 관계 정의
    legislator = relationship("Legislator", back_populates="sns")