import sys
import os

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 순환 참조 해결을 위해 모든 모델을 명시적으로 import
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

# 그 다음에 나머지 import
from app.db.database import SessionLocal
from sqlalchemy import func  # SQL 함수를 위해 추가

def check_keyword_data():
    """DB에 저장된 키워드 데이터 확인"""
    db = SessionLocal()
    try:
        # 전체 통계
        total_keywords = db.query(SpeechKeyword).count()
        unique_keywords = db.query(SpeechKeyword.keyword).distinct().count()
        legislators_with_keywords = db.query(SpeechKeyword.legislator_id).distinct().count()
        
        print("=== 키워드 데이터 통계 ===")
        print(f"총 키워드 항목 수: {total_keywords}개")
        print(f"고유 키워드 수: {unique_keywords}개")
        print(f"키워드 데이터가 있는 의원 수: {legislators_with_keywords}명")
        
        # 의원별 키워드 통계 (상위 10명)
        print("\n=== 의원별 키워드 수 (상위 10명) ===")
        keyword_counts = db.query(
            Legislator.hg_nm,
            func.count(SpeechKeyword.id).label('keyword_count')
        ).join(
            SpeechKeyword, Legislator.id == SpeechKeyword.legislator_id
        ).group_by(
            Legislator.id, Legislator.hg_nm
        ).order_by(
            func.count(SpeechKeyword.id).desc()
        ).limit(10).all()
        
        for i, (name, count) in enumerate(keyword_counts, 1):
            print(f"{i}. {name}: {count}개 키워드")
        
        # 가장 많이 발언된 키워드 (전체 의원 기준)
        print("\n=== 가장 많이 발언된 키워드 TOP 20 ===")
        top_keywords = db.query(
            SpeechKeyword.keyword,
            func.sum(SpeechKeyword.count).label('total_count')
        ).group_by(
            SpeechKeyword.keyword
        ).order_by(
            func.sum(SpeechKeyword.count).desc()
        ).limit(20).all()
        
        for i, (keyword, count) in enumerate(top_keywords, 1):
            print(f"{i}. '{keyword}': {count}회")
        
        # 특정 의원의 키워드 예시 (첫 번째 의원)
        print("\n=== 예시: 특정 의원의 키워드 ===")
        sample_legislator = db.query(Legislator).join(
            SpeechKeyword, Legislator.id == SpeechKeyword.legislator_id
        ).first()
        
        if sample_legislator:
            print(f"의원명: {sample_legislator.hg_nm}")
            keywords = db.query(SpeechKeyword).filter(
                SpeechKeyword.legislator_id == sample_legislator.id
            ).order_by(
                SpeechKeyword.count.desc()
            ).limit(10).all()
            
            for i, keyword in enumerate(keywords, 1):
                print(f"{i}. '{keyword.keyword}': {keyword.count}회")
        
        # 키워드 데이터가 없는 의원 수
        total_legislators = db.query(Legislator).count()
        legislators_without_keywords = total_legislators - legislators_with_keywords
        
        print(f"\n=== 키워드 데이터가 없는 의원 ===")
        print(f"총 {legislators_without_keywords}명 (전체 {total_legislators}명 중)")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_keyword_data()