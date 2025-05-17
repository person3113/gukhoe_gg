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
    의정발언 점수 계산 - 로그 스케일 적용
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
        import math
        for legislator in legislators:
            # 발언 횟수 로그 정규화 (100점 만점)
            speech_count = speech_data.get(legislator.id, 0)
            
            # 발언 수가 0인 경우 처리
            if speech_count == 0:
                normalized_score = 0
            else:
                # 로그 스케일 사용 (상한값을 100으로 조정)
                log_max = math.log(max_speech_count + 1)  # +1로 log(0) 방지
                log_current = math.log(speech_count + 1)  # +1로 log(0) 방지
                normalized_score = (log_current / log_max) * 100
            
            # 최소 점수 설정 (0점 방지)
            normalized_score = max(normalized_score, 5)
            
            # DB 업데이트
            legislator.speech_score = normalized_score
        
        # 변경사항 저장
        db.commit()
        print(f"의정발언 점수 계산 완료: {len(legislators)}명")
        
        # 간단한 통계 정보 출력
        avg_score = sum(legislator.speech_score for legislator in legislators) / len(legislators)
        print(f"의정발언 점수 평균: {avg_score:.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"의정발언 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_voting_scores(db: Session):
    """
    표결 책임성 점수 계산
    - 표결 참여율 계산: (기권표+불참 제외 나머지) / 전체 표결 × 100
    - 감점 요소 반영: 표결 참여율 - (기권 횟수 × 0.5 + 불참 횟수 × 1.0) / 전체 표결 수 × 10
    - 최소 0점, 최대 100점으로 제한
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        # 의원별 표결 데이터 처리
        for legislator in legislators:
            # 해당 의원의 모든 표결 결과 조회
            vote_results = db.query(VoteResult).filter(
                VoteResult.legislator_id == legislator.id
            ).all()
            
            # 표결 데이터가 없는 경우
            if not vote_results:
                # 데이터 없음 = 0점 처리
                legislator.voting_score = 0
                continue
            
            # 전체 표결 수
            total_votes = len(vote_results)
            
            # 각 유형별 표결 수 계산
            participation_count = 0  # 참여 (찬성 또는 반대)
            abstention_count = 0     # 기권
            absent_count = 0         # 불참
            
            for result in vote_results:
                if result.result_vote_mod in ["찬성", "반대"]:
                    participation_count += 1
                elif result.result_vote_mod == "기권":
                    abstention_count += 1
                else:  # 불참 또는 기타
                    absent_count += 1
            
            # 표결 참여율 계산 (0-100 범위)
            participation_rate = (participation_count / total_votes) * 100 if total_votes > 0 else 0
            
            # 감점 요소 계산 (0-100 범위)
            penalty = ((abstention_count * 0.5 + absent_count * 1.0) / total_votes) * 10 if total_votes > 0 else 0
            
            # 최종 표결 책임성 점수 계산 (감점 적용)
            voting_score = participation_rate - penalty
            
            # 최소 0점, 최대 100점으로 제한
            voting_score = max(0, min(100, voting_score))
            
            # DB에 점수 업데이트
            legislator.voting_score = voting_score
        
        # 변경사항 저장
        db.commit()
        print(f"표결 책임성 점수 계산 완료: {len(legislators)}명")
        
        # 간단한 통계 출력
        avg_score = sum(leg.voting_score for leg in legislators if leg.voting_score is not None) / len([leg for leg in legislators if leg.voting_score is not None])
        print(f"표결 책임성 점수 평균: {avg_score:.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"표결 책임성 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_cooperation_scores(db: Session):
    """
    협치/초당적 활동 점수 계산 - 이념 성향에 따른 가중치 적용
    """
    try:
        # SQLAlchemy text() 함수 임포트 추가
        from sqlalchemy import text
        
        # 진보/보수 정당 구분
        progressive_parties = ["조국혁신당", "더불어민주당", "기본소득당", "진보당", "사회민주당"]
        conservative_parties = ["국민의힘", "개혁신당"]
        
        # 모든 의원과 그들의 정당 정보를 한 번에 조회하여 캐싱
        all_legislators = db.query(Legislator).all()
        legislator_parties = {leg.id: leg.poly_nm for leg in all_legislators}
        
        # 무소속 의원 매핑
        independent_mapping = {
            "김상욱": "국민의힘",
            "우원식": "더불어민주당",
            "김종민": "더불어민주당"
        }
        
        # 각 의원별 이념 성향 캐싱
        legislator_ideologies = {}
        for leg_id, party in legislator_parties.items():
            leg = next((l for l in all_legislators if l.id == leg_id), None)
            
            # 무소속 처리
            if party == "무소속" and leg and leg.hg_nm in independent_mapping:
                party = independent_mapping[leg.hg_nm]
            
            if party in progressive_parties:
                legislator_ideologies[leg_id] = "progressive"
            elif party in conservative_parties:
                legislator_ideologies[leg_id] = "conservative"
            else:
                legislator_ideologies[leg_id] = "other"
        
        # 각 의원별 점수 계산
        for legislator in all_legislators:
            # 의원 자신의 성향
            leg_id = legislator.id
            leg_ideology = legislator_ideologies.get(leg_id, "other")
            
            # 해당 의원이 함께 발의한 다른 의원들의 정당 통계 가져오기
            # text() 함수로 SQL 쿼리 감싸기
            coworker_query = text("""
            SELECT b.legislator_id, COUNT(*) as count
            FROM bill_co_proposers a
            JOIN bill_co_proposers b ON a.bill_id = b.bill_id AND b.legislator_id != :leg_id
            WHERE a.legislator_id = :leg_id
            GROUP BY b.legislator_id
            """)
            
            coworkers = db.execute(coworker_query, {"leg_id": leg_id}).fetchall()
            
            if not coworkers:
                legislator.cooperation_score = 0
                continue
            
            # 성향 다른 의원과의 협력 비율 계산
            total_cooperations = sum(count for _, count in coworkers)
            weighted_score = 0
            
            for coworker_id, count in coworkers:
                coworker_ideology = legislator_ideologies.get(coworker_id, "other")
                
                # 다른 이념 성향과의 협력은 높은 가중치
                if leg_ideology != coworker_ideology and leg_ideology != "other" and coworker_ideology != "other":
                    weighted_score += count * 3
                # 같은 이념 성향의 다른 정당과의 협력은 낮은 가중치
                elif legislator_parties.get(leg_id) != legislator_parties.get(coworker_id):
                    weighted_score += count * 1
            
            # 총 협력 수로 나누어 가중 평균 구하기
            cooperation_score = min((weighted_score / total_cooperations) * 33.33, 100)
            
            # DB 업데이트
            legislator.cooperation_score = cooperation_score
        
        # 변경사항 저장
        db.commit()
        print(f"협치/초당적 활동 점수 계산 완료: {len(all_legislators)}명")
        
        # 간단한 통계 출력
        valid_scores = [leg.cooperation_score for leg in all_legislators if leg.cooperation_score is not None]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            print(f"협치/초당적 활동 점수 평균: {avg_score:.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"협치/초당적 활동 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def calculate_overall_scores(db: Session):
    """
    종합 점수 계산 - 각 스탯에 스케일된 값 저장 및 종합 점수 계산
    """
    try:
        # 모든 의원 조회
        legislators = db.query(Legislator).all()
        
        print("종합 점수 계산 시작...")
        
        # 각 카테고리별 현재 계산된 점수의 통계 분석
        # (NULL이 아닌 값만 대상으로)
        category_stats = {}
        
        # 각 카테고리별로 통계 계산
        for category in ['participation_score', 'legislation_score', 'speech_score', 
                         'voting_score', 'cooperation_score']:
            # NULL이 아닌 점수만 필터링
            non_null_values = [getattr(leg, category) for leg in legislators 
                              if getattr(leg, category) is not None]
            
            if non_null_values:
                category_stats[category] = {
                    'min': min(non_null_values),
                    'max': max(non_null_values),
                    'avg': sum(non_null_values) / len(non_null_values),
                    'count': len(non_null_values)
                }
                print(f"{category}: 최소={category_stats[category]['min']:.1f}, "
                      f"최대={category_stats[category]['max']:.1f}, "
                      f"평균={category_stats[category]['avg']:.1f}, "
                      f"개수={category_stats[category]['count']}")
            else:
                category_stats[category] = {
                    'min': 0,
                    'max': 0,
                    'avg': 0,
                    'count': 0
                }
                print(f"{category}: 계산된 값 없음")
        
        # 시각적 효과를 위한 목표 분포 설정
        TARGET_MIN = 5  # 최소 점수
        TARGET_MAX = 100  # 최대 점수
        
        # 의원별 종합 점수 계산 및 DB 업데이트
        for legislator in legislators:
            # 각 카테고리별 스케일링 적용
            scaled_scores = {}
            
            for category in ['participation_score', 'legislation_score', 'speech_score', 
                            'voting_score', 'cooperation_score']:
                # 원본 점수 (NULL인 경우 None 그대로 유지)
                original_score = getattr(legislator, category)
                
                # 해당 카테고리의 통계 정보
                stats = category_stats[category]
                
                # 스케일링 적용 조건: 
                # 1. 원본 점수가 있고 (NULL이 아님)
                # 2. 해당 카테고리의 최대값과 최소값이 다르며 (분포가 있음)
                # 3. 계산된 값이 하나 이상 있음
                if (original_score is not None and 
                    stats['max'] != stats['min'] and 
                    stats['count'] > 0):
                    
                    # 최소-최대 정규화 후 목표 범위로 스케일링
                    normalized = (original_score - stats['min']) / (stats['max'] - stats['min'])
                    scaled = TARGET_MIN + normalized * (TARGET_MAX - TARGET_MIN)
                    scaled_scores[category] = scaled
                    
                    # 스케일된 점수 저장 (각 스탯에 직접 반영)
                    setattr(legislator, category, scaled)
                elif original_score is None:
                    # NULL인 경우 그대로 유지
                    scaled_scores[category] = None
                else:
                    # 분포가 없거나 단일 값인 경우 (최대=최소) TARGET_MIN으로 설정
                    scaled_scores[category] = TARGET_MIN
                    setattr(legislator, category, TARGET_MIN)
            
            # 종합 점수 계산 (NULL이면 0으로 처리)
            participation = scaled_scores['participation_score'] or 0
            legislation = scaled_scores['legislation_score'] or 0
            speech = scaled_scores['speech_score'] or 0
            voting = scaled_scores['voting_score'] or 0
            cooperation = scaled_scores['cooperation_score'] or 0
            
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
        
    except Exception as e:
        db.rollback()
        print(f"종합 점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def update_tiers(db: Session):
    """
    종합 점수 분포에 따른 티어 할당
    
    Args:
        db: 데이터베이스 세션
    """
    try:
        print("티어 업데이트 시작...")
        
        # 티어 서비스 인스턴스 생성
        tier_service = TierService(db)
        
        # 의원들을 종합점수 기준으로 내림차순 정렬
        legislators = db.query(Legislator).order_by(Legislator.overall_score.desc()).all()
        
        if not legislators:
            print("티어 업데이트 실패: 의원 데이터가 없습니다.")
            return
        
        total_legislators = len(legislators)
        print(f"총 {total_legislators}명의 의원 티어를 업데이트합니다.")
        
        # 각 티어의 목표 인원수 계산
        tier_limits = {}
        accumulated = 0
        
        for tier, percentage in tier_service.tiers.items():
            # 각 티어별 의원 수 계산 (비율에 따라)
            count = round(total_legislators * percentage / 100)
            tier_limits[tier] = {
                'start': accumulated,
                'end': accumulated + count - 1  # 인덱스는 0부터 시작하므로 -1
            }
            accumulated += count
        
        # 모든 티어를 합했을 때 전체 의원수와 맞지 않는 경우 보정
        if accumulated != total_legislators:
            # 남은 인원을 마지막 티어에 추가
            last_tier = list(tier_limits.keys())[-1]
            tier_limits[last_tier]['end'] += (total_legislators - accumulated)
        
        # 각 의원의 티어 할당
        for i, legislator in enumerate(legislators):
            # 해당 인덱스가 속하는 티어 찾기
            assigned_tier = None
            for tier, limit in tier_limits.items():
                if limit['start'] <= i <= limit['end']:
                    assigned_tier = tier
                    break
            
            # 티어 업데이트
            if assigned_tier:
                legislator.tier = assigned_tier
        
        # 변경사항 저장
        db.commit()
        
        # 티어 분포 통계 출력
        tier_distribution = {}
        for legislator in legislators:
            if legislator.tier in tier_distribution:
                tier_distribution[legislator.tier] += 1
            else:
                tier_distribution[legislator.tier] = 1
        
        print("티어 분포:")
        for tier, count in tier_distribution.items():
            percentage = (count / total_legislators) * 100
            print(f"  {tier}: {count}명 ({percentage:.1f}%)")
        
        print("티어 업데이트 완료")
        
    except Exception as e:
        db.rollback()
        print(f"티어 업데이트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def update_rankings(db: Session):
    """
    종합 점수 기준 순위(overall_rank) 업데이트
    
    Args:
        db: 데이터베이스 세션
    """
    try:
        print("랭킹 업데이트 시작...")
        
        # 종합 점수 기준으로 의원들을 내림차순 정렬
        legislators = db.query(Legislator).order_by(Legislator.overall_score.desc()).all()
        
        if not legislators:
            print("랭킹 업데이트 실패: 의원 데이터가 없습니다.")
            return
        
        # 순위 할당 (동점자는 같은 순위 적용)
        current_rank = 1
        previous_score = None
        skipped_ranks = 0
        
        for i, legislator in enumerate(legislators):
            current_score = legislator.overall_score
            
            # 점수가 없는 경우 가장 낮은 순위 부여
            if current_score is None:
                legislator.overall_rank = len(legislators)
                continue
            
            # 이전 점수와 비교 (첫 번째 의원 또는 점수가 다른 경우)
            if previous_score is None or current_score != previous_score:
                # 새로운 순위 = 현재 기본 순위 + 건너뛴 순위 수
                current_rank = i + 1
                skipped_ranks = 0
            else:
                # 동점자는 같은 순위 유지 (skipped_ranks는 증가하지 않음)
                skipped_ranks += 1
            
            # 순위 업데이트
            legislator.overall_rank = current_rank
            
            # 현재 점수를 이전 점수로 저장
            previous_score = current_score
        
        # 변경사항 저장
        db.commit()
        
        # 간단한 통계 출력
        min_rank = min(leg.overall_rank for leg in legislators if leg.overall_rank is not None)
        max_rank = max(leg.overall_rank for leg in legislators if leg.overall_rank is not None)
        
        print(f"총 {len(legislators)}명의 의원 랭킹 업데이트 완료 (순위 범위: {min_rank}-{max_rank})")
        
    except Exception as e:
        db.rollback()
        print(f"랭킹 업데이트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calculate_all_scores()