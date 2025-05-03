from pydantic import BaseModel
from typing import Optional, List

class LegislatorBase(BaseModel):
    # 기본 정보 필드
    mona_cd: str
    hg_nm: str
    eng_nm: Optional[str] = None
    bth_date: Optional[str] = None
    job_res_nm: Optional[str] = None
    poly_nm: str
    orig_nm: str
    cmit_nm: Optional[str] = None
    reele_gbn_nm: str
    sex_gbn_nm: str
    tel_no: Optional[str] = None
    e_mail: Optional[str] = None
    mem_title: Optional[str] = None
    profile_image_url: Optional[str] = None

class LegislatorCreate(LegislatorBase):
    # 생성 시 필요한 추가 필드
    pass

class LegislatorUpdate(BaseModel):
    # 업데이트 가능한 필드
    hg_nm: Optional[str] = None
    eng_nm: Optional[str] = None
    bth_date: Optional[str] = None
    job_res_nm: Optional[str] = None
    poly_nm: Optional[str] = None
    orig_nm: Optional[str] = None
    cmit_nm: Optional[str] = None
    reele_gbn_nm: Optional[str] = None
    sex_gbn_nm: Optional[str] = None
    tel_no: Optional[str] = None
    e_mail: Optional[str] = None
    mem_title: Optional[str] = None
    profile_image_url: Optional[str] = None
    tier: Optional[str] = None
    overall_rank: Optional[int] = None
    participation_score: Optional[float] = None
    legislation_score: Optional[float] = None
    speech_score: Optional[float] = None
    voting_score: Optional[float] = None
    cooperation_score: Optional[float] = None
    overall_score: Optional[float] = None
    asset: Optional[int] = None

class LegislatorInDB(LegislatorBase):
    # DB에서 조회한 데이터
    id: int
    tier: Optional[str] = None
    overall_rank: Optional[int] = None
    participation_score: Optional[float] = None
    legislation_score: Optional[float] = None
    speech_score: Optional[float] = None
    voting_score: Optional[float] = None
    cooperation_score: Optional[float] = None
    overall_score: Optional[float] = None
    asset: Optional[int] = None

    class Config:
        orm_mode = True

class Legislator(LegislatorInDB):
    # API 응답용 모델
    pass

class LegislatorDetail(Legislator):
    # 상세 정보 조회 시 사용
    sns: Optional['SNSInfo'] = None
    
    class Config:
        orm_mode = True

class SNSInfo(BaseModel):
    # SNS 정보 모델
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    youtube_url: Optional[str] = None
    blog_url: Optional[str] = None

    class Config:
        orm_mode = True