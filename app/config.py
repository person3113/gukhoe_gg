# app/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///:memory:" if os.getenv("DB_MODE") == "memory" else "sqlite:///./data/db.sqlite"
    
    # API 키 설정
    API_KEY: str = os.getenv("ASSEMBLY_API_KEY", "sample")
    
    # API 기본 URL
    BASE_API_URL: str = "https://open.assembly.go.kr/portal/openapi/"
    
    # API 엔드포인트들
    API_ENDPOINTS: dict = {
        "legislator_info": "nwvrqwxyaytdsfvhu",    # 국회의원 인적사항
        "legislator_sns": "negnlnyvatsjwocar",     # 국회의원 SNS정보
        "committee_members": "nktulghcadyhmiqxi",  # 위원회 위원 명단
        "committee_info": "nxrvzonlafugpqjuh",     # 위원회 현황 정보
        "bills": "nzmimeepazxkubdpn",             # 국회의원 발의법률안
        "processed_bills_stats": "BILLCNTCMIT",   # 처리 의안통계(위원회별)
        "processed_bills": "nzpltgfqabtcpsmai",   # 법률안 심사 및 처리(처리의안)
        "processed_assembly_bills": "nwbpacrgavhjryiph", # 본회의 처리안건_법률안
        "vote_results": "nojepdqqaweusdfbi",      # 국회의원 본회의 표결정보
        "committee_history": "nyzrglyvagmrypezq"  # 국회의원 위원회 경력
    }
    
    # 공통 API 요청 인자
    DEFAULT_API_ARGS: dict = {
        "Type": "xml",  # 기본 응답 형식
        "pIndex": "1",  # 기본 페이지 인덱스
        "pSize": "100"  # 기본 페이지 크기
    }
    
    # API별 필수 인자
    API_REQUIRED_ARGS: dict = {
        "processed_bills": {"AGE": "22"},  # 법률안 심사 및 처리(처리의안) - 대수 필수
        "processed_assembly_bills": {"AGE": "22"},  # 본회의 처리안건_법률안 - 대수 필수
        "vote_results": {"AGE": "22", "BILL_ID": None},  # 본회의 표결정보 - 대수 및 의안ID 필수
        "processed_bills_stats": {"ERACO": "제22대"}  # 처리 의안통계(위원회별) - 대수 필수
    }
    
    # Pydantic 2.x에서 Config 클래스 대신 model_config 사용
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # 추가 필드 허용 (assembly_api_key 등)
    )

settings = Settings()