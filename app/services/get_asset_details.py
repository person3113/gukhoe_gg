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
    
    # 카테고리명 줄임말 매핑
    category_abbreviations = {
        "정치자금법에 따른 정치자금의 수입 및 지출을 위한 예금계좌의 예금": "정치자금 예금",
        "부동산에 관한 규정이 준용되는 권리와 자동차·건설기계·선박 및 항공기": "부동산 준용 권리"
    }
    
    # 원래 카테고리명 저장 (설명용)
    original_category_names = {}
    for abbr_key, abbr_value in category_abbreviations.items():
        original_category_names[abbr_value] = abbr_key
    
    # 카테고리별 자산 합계 계산
    category_totals = {}
    for detail in asset_details:
        # 원래 카테고리명 저장
        original_category = detail.asset_category
        
        # 줄임말로 변환
        category = category_abbreviations.get(original_category, original_category)
        
        if category not in category_totals:
            category_totals[category] = 0.0  # float 타입으로 초기화
        category_totals[category] += float(detail.asset_current) if detail.asset_current else 0.0
    
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
        # 원래 카테고리명 저장
        original_category = detail.asset_category
        # 줄임말로 변환
        abbreviated_category = category_abbreviations.get(original_category, original_category)
        
        result["asset_details"].append({
            "asset_category": abbreviated_category,
            "original_category": original_category,  # 원래 카테고리명도 함께 저장
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
    # 총 자산 계산
    total_asset_value = sum(category_totals.values())
    
    # 줄임말로 변환된 카테고리에 대한 원래 카테고리명 추가
    for category, total in category_totals.items():
        # 비율 계산 (백분율)
        percentage = 0.0
        if total_asset_value > 0:
            percentage = (float(total) / float(total_asset_value)) * 100.0
        
        # 원래 카테고리명 찾기 (줄임말이 있는 경우)
        original_name = original_category_names.get(category, "")
            
        result["category_totals"].append({
            "category": category,
            "original_category": original_name,  # 원래 카테고리명 추가
            "total": round(float(total) / 1000.0, 1),  # 백만원 단위로 변환, 소수점 유지
            "percentage": round(percentage, 1)  # 소수점 첨째 자리까지 반올림
        })
    
    # 카테고리별 합계를 금액 기준으로 내림차순 정렬
    result["category_totals"] = sorted(result["category_totals"], key=lambda x: x["total"], reverse=True)
    
    return result
