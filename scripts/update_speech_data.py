# scripts/update_speech_data.py 수정

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 모든 모델을 명시적으로 import (순환 참조 문제 해결)
from app.models.legislator import Legislator
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.sns import LegislatorSNS
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

from app.db.database import SessionLocal
from scripts.fetch_data import fetch_excel_data

def update_speech_data():
    """수동으로 회의별 발언수 데이터 업데이트"""
    db = SessionLocal()
    try:
        print("회의별 발언수 데이터 업데이트 시작...")
        fetch_excel_data(db)
        print("업데이트 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_speech_data()