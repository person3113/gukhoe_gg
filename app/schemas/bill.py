from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class BillBase(BaseModel):
    # 기본 정보 필드
    bill_no: str
    bill_name: str
    propose_dt: str
    detail_link: Optional[str] = None
    proposer: str
    committee: Optional[str] = None
    proc_result: Optional[str] = None

class BillCreate(BillBase):
    # 생성 시 필요한 추가 필드
    main_proposer_id: int

class BillUpdate(BaseModel):
    # 업데이트 가능한 필드
    bill_name: Optional[str] = None
    propose_dt: Optional[str] = None
    detail_link: Optional[str] = None
    proposer: Optional[str] = None
    committee: Optional[str] = None
    proc_result: Optional[str] = None
    main_proposer_id: Optional[int] = None

class BillInDB(BillBase):
    # DB에서 조회한 데이터
    id: int
    main_proposer_id: int

    class Config:
        orm_mode = True

class Bill(BillInDB):
    # API 응답용 모델
    pass

class BillDetail(Bill):
    # 상세 정보 조회 시 사용
    main_proposer: 'LegislatorBasic'
    co_proposers: List['LegislatorBasic'] = []
    
    class Config:
        orm_mode = True

class BillCoProposerCreate(BaseModel):
    # 공동발의자 생성 모델
    bill_id: int
    legislator_id: int

class BillCoProposer(BillCoProposerCreate):
    # 공동발의자 모델
    id: int
    
    class Config:
        orm_mode = True

# 순환 참조 문제 해결을 위한 간소화된 의원 정보 모델
class LegislatorBasic(BaseModel):
    id: int
    hg_nm: str
    poly_nm: str
    
    class Config:
        orm_mode = True