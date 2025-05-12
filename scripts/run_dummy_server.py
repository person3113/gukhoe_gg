import sys
import os
import uvicorn

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 메모리 DB 설정을 위한 환경 변수 설정
os.environ["DB_MODE"] = "memory"

# create_dummy_data.py 수정도 필요함 - 여기서는 import만 수행
from scripts.create_dummy_data import init_db, create_dummy_data

if __name__ == "__main__":
    # 서버 실행
    print("서버를 실행합니다...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)