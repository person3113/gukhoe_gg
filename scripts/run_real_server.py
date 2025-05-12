import sys
import os
import uvicorn

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 환경 변수 설정
os.environ["DB_MODE"] = "real_test" 

# 모든 모델을 명시적으로 임포트하여 순환 참조 문제 해결
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

if __name__ == "__main__":
    # 서버 실행
    print("서버를 실행합니다...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)