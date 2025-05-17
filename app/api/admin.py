from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.templating import Jinja2Templates
import os

from app.db.database import get_db, SessionLocal
from scripts.calculate_scores import (
    calculate_all_scores,
    calculate_participation_scores,
    calculate_legislation_scores,
    calculate_speech_scores,
    calculate_voting_scores,
    calculate_cooperation_scores,
    calculate_overall_scores,
    update_tiers,
    update_rankings
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.post("/calculate-scores")
async def api_calculate_scores(
    background_tasks: BackgroundTasks,
    category: Optional[str] = None,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    점수 계산 API
    
    Args:
        background_tasks: 백그라운드 작업 객체
        category: 계산할 카테고리 (None인 경우 전체 계산)
        force: 강제 재계산 여부 (데이터 변경 여부 무시)
        db: 데이터베이스 세션
    
    Returns:
        계산 시작 메시지
    """
    # 백그라운드에서 점수 계산 실행
    background_tasks.add_task(
        calculate_scores_task, 
        category=category,
        force=force
    )
    
    # 즉시 응답 반환
    if category:
        return {"message": f"{category} 카테고리 점수 계산이 백그라운드에서 시작되었습니다."}
    else:
        return {"message": "전체 점수 계산이 백그라운드에서 시작되었습니다."}

@router.get("/dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """관리자 대시보드 페이지"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

async def calculate_scores_task(category: Optional[str] = None, force: bool = False):
    """
    백그라운드에서 실행될 점수 계산 작업
    
    Args:
        category: 계산할 카테고리
        force: 강제 재계산 여부
    """
    db = SessionLocal()
    try:
        if category:
            # 특정 카테고리만 계산
            if category == "participation":
                need_update = check_data_changes(db, category) or force
                if need_update:
                    print("참여 점수 계산 시작...")
                    calculate_participation_scores(db)
            elif category == "legislation":
                need_update = check_data_changes(db, category) or force
                if need_update:
                    print("입법활동 점수 계산 시작...")
                    calculate_legislation_scores(db)
            elif category == "speech":
                need_update = check_data_changes(db, category) or force
                if need_update:
                    print("의정발언 점수 계산 시작...")
                    calculate_speech_scores(db)
            elif category == "voting":
                need_update = check_data_changes(db, category) or force
                if need_update:
                    print("표결 책임성 점수 계산 시작...")
                    calculate_voting_scores(db)
            elif category == "cooperation":
                need_update = check_data_changes(db, category) or force
                if need_update:
                    print("협치/초당적 활동 점수 계산 시작...")
                    calculate_cooperation_scores(db)
            elif category == "overall":
                print("종합 점수 계산 시작...")
                calculate_overall_scores(db)
                update_tiers(db)
                update_rankings(db)
            else:
                print(f"알 수 없는 카테고리: {category}")
                return
            
            # 개별 카테고리 계산 후 종합 점수 자동 업데이트
            if category != "overall":
                print("종합 점수 업데이트...")
                calculate_overall_scores(db)
                update_tiers(db)
                update_rankings(db)
        else:
            # 전체 점수 계산
            print("전체 점수 계산 시작...")
            any_update = False
            
            # 각 카테고리별 데이터 변경 확인 및 계산
            for cat in ["participation", "legislation", "speech", "voting", "cooperation"]:
                need_update = check_data_changes(db, cat) or force
                if need_update:
                    any_update = True
                    if cat == "participation":
                        calculate_participation_scores(db)
                    elif cat == "legislation":
                        calculate_legislation_scores(db)
                    elif cat == "speech":
                        calculate_speech_scores(db)
                    elif cat == "voting":
                        calculate_voting_scores(db)
                    elif cat == "cooperation":
                        calculate_cooperation_scores(db)
            
            # 데이터 변경이 있거나 강제 재계산인 경우에만 종합 점수 계산
            if any_update or force:
                calculate_overall_scores(db)
                update_tiers(db)
                update_rankings(db)
            else:
                print("변경된 데이터가 없습니다. 점수 계산을 건너뜁니다.")
        
        print("점수 계산 완료!")
    except Exception as e:
        print(f"점수 계산 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_data_changes(db: Session, category: str) -> bool:
    """
    특정 카테고리와 관련된 데이터 변경 여부 확인
    
    Args:
        db: 데이터베이스 세션
        category: 점수 카테고리
    
    Returns:
        데이터 변경 여부 (True: 변경됨, False: 변경 없음)
    """
    from app.models.legislator import Legislator
    from app.models.bill import Bill, BillCoProposer
    from app.models.attendance import Attendance
    from app.models.vote import Vote, VoteResult
    from app.models.speech import SpeechKeyword, SpeechByMeeting
    
    try:
        # 전체 의원 수 (기준값)
        total_legislators = db.query(Legislator).count()
        
        if category == "participation":
            # 출석 데이터 확인
            attendance_count = db.query(Attendance).count()
            # 의원별 점수가 모두 계산되었는지 확인
            calculated_count = db.query(Legislator).filter(
                Legislator.participation_score != None
            ).count()
            
            # 의원 수와 계산된 점수 수가 다르거나, 출석 데이터가 0인 경우 변경으로 판단
            return calculated_count < total_legislators or attendance_count == 0
            
        elif category == "legislation":
            # 법안 데이터 확인
            bill_count = db.query(Bill).count()
            co_proposer_count = db.query(BillCoProposer).count()
            
            # 점수가 계산된 의원 수 확인
            calculated_count = db.query(Legislator).filter(
                Legislator.legislation_score != None
            ).count()
            
            # 의원 수와 계산된 점수 수가 다르거나, 법안 데이터가 0인 경우 변경으로 판단
            return calculated_count < total_legislators or bill_count == 0
            
        elif category == "speech":
            # 발언 데이터 확인
            speech_count = db.query(SpeechByMeeting).count()
            keyword_count = db.query(SpeechKeyword).count()
            
            # 점수가 계산된 의원 수 확인
            calculated_count = db.query(Legislator).filter(
                Legislator.speech_score != None
            ).count()
            
            # 의원 수와 계산된 점수 수가 다르거나, 발언 데이터가 0인 경우 변경으로 판단
            return calculated_count < total_legislators or speech_count == 0
            
        elif category == "voting":
            # 표결 데이터 확인
            vote_count = db.query(Vote).count()
            vote_result_count = db.query(VoteResult).count()
            
            # 점수가 계산된 의원 수 확인
            calculated_count = db.query(Legislator).filter(
                Legislator.voting_score != None
            ).count()
            
            # 의원 수와 계산된 점수 수가 다르거나, 표결 데이터가 0인 경우 변경으로 판단
            return calculated_count < total_legislators or vote_count == 0
            
        elif category == "cooperation":
            # 공동발의 데이터 확인
            co_proposer_count = db.query(BillCoProposer).count()
            
            # 점수가 계산된 의원 수 확인
            calculated_count = db.query(Legislator).filter(
                Legislator.cooperation_score != None
            ).count()
            
            # 의원 수와 계산된 점수 수가 다르거나, 공동발의 데이터가 0인 경우 변경으로 판단
            return calculated_count < total_legislators or co_proposer_count == 0
            
        return False  # 기본값: 변경 없음
        
    except Exception as e:
        print(f"데이터 변경 확인 중 오류 발생: {str(e)}")
        return True  # 오류 발생 시 안전하게 변경됨으로 간주