from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models.legislator import Legislator
from app.models.assetdetailed import AssetDetailed

def get_legislator_asset_details(db: Session, legislator_id: int) -> Dict[str, Any]:
    """
    특정 의원의 재산 상세 정보 조회
    
    Args:
        db: 데이터베이스 세션
        legislator_id: 의원 ID
        
    Returns:
        의원 재산 상세 정보
    """
    # 의원 기본 정보 조회
    legislator = db.query(
        Legislator.id,
        Legislator.hg_nm.label("name"),
        Legislator.poly_nm.label("party"),
        Legislator.reele_gbn_nm.label("term"),
        Legislator.cmit_nm.label("committee"),
        Legislator.asset.label("asset"),
        Legislator.mona_cd.label("mona_cd")
    ).filter(
        Legislator.id == legislator_id
    ).first()
    
    if not legislator:
        return None
    
    # 의원 재산 상세 정보 조회
    asset_details = db.query(
        AssetDetailed.asset_category,
        AssetDetailed.relation_to_self,
        AssetDetailed.asset_type,
        AssetDetailed.location,
        AssetDetailed.area_sqm,
        AssetDetailed.asset_previous,
        AssetDetailed.asset_current,
        AssetDetailed.asset_increase,
        AssetDetailed.asset_decrease,
        AssetDetailed.reason_for_change
    ).filter(
        AssetDetailed.mona_code == legislator.mona_cd
    ).order_by(
        AssetDetailed.asset_current.desc()
    ).all()
    
    # 카테고리별 자산 합계 계산
    category_totals = {}
    for detail in asset_details:
        category = detail.asset_category
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += detail.asset_current if detail.asset_current else 0
    
    # 결과 딕셔너리 생성
    result = {
        "legislator": {
            "id": legislator.id,
            "name": legislator.name,
            "party": legislator.party,
            "term": legislator.term,
            "committee": legislator.committee,
            "asset": round(legislator.asset / 100000000, 1) if legislator.asset else 0  # 억원 단위로 변환
        },
        "asset_details": [],
        "category_totals": []
    }
    
    # 자산 상세 정보 변환
    for detail in asset_details:
        result["asset_details"].append({
            "asset_category": detail.asset_category,
            "relation_to_self": detail.relation_to_self,
            "asset_type": detail.asset_type,
            "location": detail.location,
            "area_sqm": detail.area_sqm,
            "asset_previous": round(detail.asset_previous / 1000, 1) if detail.asset_previous else 0,  # 백만원 단위로 변환
            "asset_current": round(detail.asset_current / 1000, 1) if detail.asset_current else 0,  # 백만원 단위로 변환
            "asset_increase": round(detail.asset_increase / 1000, 1) if detail.asset_increase else 0,  # 백만원 단위로 변환
            "asset_decrease": round(detail.asset_decrease / 1000, 1) if detail.asset_decrease else 0,  # 백만원 단위로 변환
            "reason_for_change": detail.reason_for_change
        })
    
    # 카테고리별 합계 변환
    for category, total in category_totals.items():
        result["category_totals"].append({
            "category": category,
            "total": round(total / 1000, 1)  # 백만원 단위로 변환
        })
    
    # 카테고리별 합계를 금액 기준으로 내림차순 정렬
    result["category_totals"] = sorted(result["category_totals"], key=lambda x: x["total"], reverse=True)
    
    return result
