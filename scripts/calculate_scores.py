import sys
import os
from sqlalchemy import func
from sqlalchemy.orm import Session

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.services.tier_service import TierService

# 먼저 모든 모델을 명시적으로 임포트하여 순환 참조 문제 해결
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def calculate_all_scores():
    """
    모든 점수 계산 함수 호출
    """
    # DB 세션 생성
    db = SessionLocal()
    try:
        print("Calculating all scores...")
        calculate_participation_scores(db)
        calculate_legislation_scores(db)
        calculate_speech_scores(db)
        calculate_voting_scores(db)
        calculate_cooperation_scores(db)
        calculate_overall_scores(db)
        update_tiers(db)
        update_rankings(db)
        print("Score calculation completed.")
    finally:
        db.close()

def calculate_participation_scores(db: Session):
    """
    참여 점수 계산
    """
    # DB에서 출석 데이터 조회
    # 의원별 출석률 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    pass

def calculate_legislation_scores(db: Session):
    """
    입법활동 점수 계산
    - 대표발의 활동량(60%): 대표발의안 수 / 최대 대표발의안 수 × 100
    - 공동발의 활동량(20%): 공동발의안 수 / 최대 공동발의안 수 × 100
    - 법안 통과 성공률(20%): (원안가결×1.2 + 수정가결×1.0 + 대안반영×0.8) / 대표발의안 수 × 100
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        # 의원별 대표발의안 수, 공동발의안 수, 대표발의 법안 처리 결과 집계
        legislator_scores = []
        max_main_count = 0
        max_co_count = 0
        
        for legislator in legislators:
            # 대표발의안 수 조회
            main_bills_count = db.query(Bill).filter(
                Bill.main_proposer_id == legislator.id
            ).count()
            
            # 공동발의안 수 조회
            co_bills_count = db.query(BillCoProposer).filter(
                BillCoProposer.legislator_id == legislator.id
            ).count()
            
            # 법안 처리 결과 집계
            bills = db.query(Bill).filter(
                Bill.main_proposer_id == legislator.id
            ).all()
            
            # 처리 결과별 합계
            original_pass = 0  # 원안가결
            modified_pass = 0  # 수정가결
            alternative = 0   # 대안반영폐기
            
            for bill in bills:
                if bill.proc_result == "원안가결":
                    original_pass += 1
                elif bill.proc_result == "수정가결":
                    modified_pass += 1
                elif bill.proc_result == "대안반영폐기":
                    alternative += 1
            
            # 의원별 데이터 저장
            legislator_scores.append({
                "id": legislator.id,
                "main_bills_count": main_bills_count,
                "co_bills_count": co_bills_count,
                "original_pass": original_pass,
                "modified_pass": modified_pass,
                "alternative": alternative
            })
            
            # 최대값 갱신
            if main_bills_count > max_main_count:
                max_main_count = main_bills_count
            if co_bills_count > max_co_count:
                max_co_count = co_bills_count
        
        # 최대값이 0인 경우 처리 (0으로 나누기 방지)
        if max_main_count == 0:
            max_main_count = 1
        if max_co_count == 0:
            max_co_count = 1
        
        # 의원별 점수 계산 및 DB 업데이트
        for score_data in legislator_scores:
            legislator_id = score_data["id"]
            
            # 대표발의 활동량 (60%)
            main_activity = (score_data["main_bills_count"] / max_main_count) * 100 * 0.6
            
            # 공동발의 활동량 (20%)
            co_activity = (score_data["co_bills_count"] / max_co_count) * 100 * 0.2
            
            # 법안 통과 성공률 (20%)
            if score_data["main_bills_count"] > 0:
                pass_rate = (
                    (score_data["original_pass"] * 1.2 + 
                     score_data["modified_pass"] * 1.0 + 
                     score_data["alternative"] * 0.8) / 
                    score_data["main_bills_count"] * 100 * 0.2
                )
            else:
                pass_rate = 0
            
            # 총점 계산 (최대 100점)
            total_score = min(main_activity + co_activity + pass_rate, 100)
            
            # DB 업데이트
            legislator = db.query(Legislator).filter(Legislator.id == legislator_id).first()
            if legislator:
                legislator.legislation_score = total_score
        
        # 변경사항 저장
        db.commit()
        print(f"입법활동 점수 계산 완료: {len(legislator_scores)}명")
        
    except Exception as e:
        db.rollback()
        print(f"입법활동 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_speech_scores(db: Session):
    """
    의정발언 점수 계산
    - 발언 횟수 정규화: (의원 발언 수 / 최대 발언 수) × 100
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        # 발언 데이터 조회 (SpeechByMeeting 테이블)
        speech_data = {}
        max_speech_count = 0
        
        # 모든 의원의 발언 횟수 조회
        for legislator in legislators:
            # 의원별 발언 횟수 조회
            speech_record = db.query(SpeechByMeeting).filter(
                SpeechByMeeting.legislator_id == legislator.id
            ).first()
            
            # 발언 횟수 저장
            speech_count = speech_record.count if speech_record else 0
            speech_data[legislator.id] = speech_count
            
            # 최대 발언 횟수 갱신
            if speech_count > max_speech_count:
                max_speech_count = speech_count
        
        # 최대값이 0인 경우 처리 (0으로 나누기 방지)
        if max_speech_count == 0:
            max_speech_count = 1
            print("경고: 최대 발언 횟수가 0입니다!")
        
        # 각 의원별 점수 계산 및 DB 업데이트
        for legislator in legislators:
            # 발언 횟수 정규화 (100점 만점)
            speech_count = speech_data.get(legislator.id, 0)
            normalized_score = (speech_count / max_speech_count) * 100
            
            # DB 업데이트
            legislator.speech_score = normalized_score
        
        # 변경사항 저장
        db.commit()
        print(f"의정발언 점수 계산 완료: {len(legislators)}명")
        
    except Exception as e:
        db.rollback()
        print(f"의정발언 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_voting_scores(db: Session):
    """
    표결 책임성 점수 계산
    """
    # DB에서 표결 데이터 조회
    # 의원별 기권률, 불참률 계산
    # 점수 산출 알고리즘 적용 (낮을수록 높은 점수)
    # DB 업데이트
    pass

def calculate_cooperation_scores(db: Session):
    """
    협치/초당적 활동 점수 계산
    """
    # DB에서 법안 공동발의 데이터 조회
    # 의원별 타 정당 의원과 공동발의 비율 계산
    # 점수 산출 알고리즘 적용
    # DB 업데이트
    pass

def calculate_overall_scores(db: Session):
    """
    종합 점수 계산 - 시각적 효과를 위한 재스케일링 적용
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        print("종합 점수 계산 시작...")
        
        # 각 카테고리별 최대값, 최소값, 평균값 계산 (NULL 제외)
        max_scores = {}
        min_scores = {}
        avg_scores = {}
        
        # 각 카테고리 점수 통계 계산
        categories = ['participation_score', 'legislation_score', 'speech_score', 
                      'voting_score', 'cooperation_score']
        
        for category in categories:
            # NULL이 아닌 점수만 필터링
            non_null_scores = [getattr(leg, category) for leg in legislators 
                              if getattr(leg, category) is not None]
            
            if non_null_scores:
                max_scores[category] = max(non_null_scores)
                min_scores[category] = min(non_null_scores)
                avg_scores[category] = sum(non_null_scores) / len(non_null_scores)
                print(f"{category} - 최대: {max_scores[category]:.1f}, 최소: {min_scores[category]:.1f}, 평균: {avg_scores[category]:.1f}")
            else:
                max_scores[category] = 0
                min_scores[category] = 0
                avg_scores[category] = 0
                print(f"{category} - 계산된 점수 없음")
        
        # 시각적 효과를 위한 목표 분포 설정
        TARGET_MIN = 15  # 최소 점수
        TARGET_MAX = 100  # 최대 점수
        TARGET_AVG = 40  # 목표 평균 점수
        
        # 각 카테고리별 스케일링 함수 생성
        def scale_score(score, category):
            if score is None or max_scores[category] == min_scores[category]:
                return TARGET_MIN  # NULL이거나 모든 점수가 같으면 최소값 반환
                
            # 최소-최대 정규화 후 목표 범위로 스케일링
            normalized = (score - min_scores[category]) / (max_scores[category] - min_scores[category])
            scaled = TARGET_MIN + normalized * (TARGET_MAX - TARGET_MIN)
            return scaled
        
        # 의원별 종합 점수 계산 및 DB 업데이트
        for legislator in legislators:
            # 각 카테고리 점수 스케일링
            participation = scale_score(legislator.participation_score, 'participation_score') if legislator.participation_score else 0
            legislation = scale_score(legislator.legislation_score, 'legislation_score') if legislator.legislation_score else 0
            speech = scale_score(legislator.speech_score, 'speech_score') if legislator.speech_score else 0
            voting = scale_score(legislator.voting_score, 'voting_score') if legislator.voting_score else 0
            cooperation = scale_score(legislator.cooperation_score, 'cooperation_score') if legislator.cooperation_score else 0
            
            # 계산된 카테고리 점수가 없으면 기본값 사용
            if not any([legislator.participation_score, legislator.legislation_score, 
                       legislator.speech_score, legislator.voting_score, legislator.cooperation_score]):
                print(f"의원 ID {legislator.id}: 계산된 카테고리 점수 없음, 기본값 사용")
                participation = TARGET_MIN
                legislation = TARGET_MIN
                speech = TARGET_MIN
                voting = TARGET_MIN
                cooperation = TARGET_MIN
            
            # 스케일링된 점수 저장 (원본은 유지하고 시각화용으로만 사용할 경우 이 부분 주석 처리)
            # legislator.participation_score = participation
            # legislator.legislation_score = legislation
            # legislator.speech_score = speech
            # legislator.voting_score = voting
            # legislator.cooperation_score = cooperation
            
            # 가중치에 따른 종합 점수 계산
            overall_score = (
                participation * 0.15 +  # 참여도 (15%)
                legislation * 0.4 +     # 입법활동 (40%)
                speech * 0.25 +         # 의정발언 (25%)
                voting * 0.1 +          # 표결 책임성 (10%)
                cooperation * 0.1       # 협치/초당적 활동 (10%)
            )
            
            # 종합 점수 저장
            legislator.overall_score = overall_score
        
        # 변경사항 저장
        db.commit()
        print(f"종합 점수 계산 완료: {len(legislators)}명")
        
        # 결과 샘플 출력
        if legislators:
            sample = legislators[0]
            print(f"샘플 의원(ID: {sample.id}) - 종합 점수: {sample.overall_score:.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"종합 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def update_tiers(db: Session):
    """
    티어 업데이트
    """
    # 호출: TierService(db).update_tiers()로 티어 업데이트
    # DB 업데이트
    pass

def update_rankings(db: Session):
    """
    랭킹 업데이트
    """
    # 호출: update_rankings()로 랭킹 업데이트
    # DB 업데이트
    pass

if __name__ == "__main__":
    calculate_all_scores()