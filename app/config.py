import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./data/db.sqlite"
    
    # API 키 설정
    API_KEY: str = os.getenv("ASSEMBLY_API_KEY", "sample")
    
    # 기타 설정
    BASE_API_URL: str = "https://open.assembly.go.kr/portal/openapi/"
    
    class Config:
        env_file = ".env"

settings = Settings()