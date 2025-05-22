from sqlalchemy import Column, Integer, String, BigInteger
from app.db.database import Base

class AssetDetailed(Base):
    __tablename__ = "assets_detailed"  # 테이블명도 통일 가능

    id = Column(Integer, primary_key=True, index=True)

    report_year_month = Column(String, index=True)  # 연월 (예: 202503)
    row_no = Column(Integer)  # 원본 엑셀 내 순번
    mona_code = Column(String, index=True)  # 국회의원 코드
    role_group = Column(String)  # 구분 (1.국회의원 등)
    affiliation = Column(String)  # 소속 (국회 등)
    position = Column(String)  # 직위 (국회의장 등)
    name = Column(String)  # 이름
    asset_category = Column(String)  # 재산구분 (토지/건물 등)
    relation_to_self = Column(String)  # 본인과의 관계
    asset_type = Column(String)  # 재산의종류 (대지, 임야 등)
    location = Column(String)  # 소재지
    area_sqm = Column(String)  # 면적 (㎡) — 텍스트형으로 유지 (예외 있음)
    rights_detail = Column(String)  # 등 권리의 명세

    asset_previous = Column(BigInteger)  # 종전 자산 (단위: 천원)
    asset_increase = Column(BigInteger)  # 증가 자산 (단위: 천원)
    asset_increase_real = Column(BigInteger, nullable=True)  # 증가 실거래가 (천원)
    asset_decrease = Column(BigInteger)  # 감소 자산 (천원)
    asset_decrease_real = Column(BigInteger, nullable=True)  # 감소 실거래가 (천원)
    asset_current = Column(BigInteger)  # 현재 자산 (천원)

    reason_for_change = Column(String)  # 변동사유