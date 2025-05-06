from typing import List, Dict, Any, Optional

def generate_top_score_chart_data(legislators: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    상위 의원들의 점수를 chart.js에서 사용 가능한 형식으로 변환하는 함수
    
    Args:
        legislators: 상위 의원 목록
        
    Returns:
        차트 데이터가 포함된 딕셔너리
    """
    # 차트에 표시할 라벨(의원 이름) 추출
    labels = [leg["name"] for leg in legislators]
    
    # 데이터값 추출
    scores = [float(leg["overall_score"]) for leg in legislators]
    
    # 각 카테고리별 데이터셋 생성
    datasets = [
        {
            "label": "종합 점수",
            "data": scores,
            "backgroundColor": "rgba(75, 192, 192, 0.6)",
            "borderColor": "rgba(75, 192, 192, 1)",
            "borderWidth": 1
        }
    ]
    
    # 차트 데이터 딕셔너리 구성
    chart_data = {
        "labels": labels,
        "datasets": datasets
    }
    
    return chart_data

def generate_comparison_chart_data(stats: Dict[str, Any], avg_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    개인 스탯과 평균 스탯을 비교 차트 데이터로 변환
    
    Args:
        stats: 의원 스탯 정보
        avg_stats: 평균 스탯 정보 (None인 경우 빈 차트 생성)
    
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트 라벨 (카테고리)
    labels = ["참여", "입법활동", "의정발언", "표결 책임성", "협치/초당적 활동"]
    
    # 의원 스탯 데이터
    personal_data = [
        stats["participation_score"],
        stats["legislation_score"],
        stats["speech_score"],
        stats["voting_score"],
        stats["cooperation_score"]
    ]
    
    # 데이터셋 구성
    datasets = [
        {
            "label": "개인 점수",
            "data": personal_data,
            "backgroundColor": "rgba(75, 192, 192, 0.6)",
            "borderColor": "rgba(75, 192, 192, 1)",
            "borderWidth": 1
        }
    ]
    
    # 평균 스탯이 제공된 경우 추가
    if avg_stats:
        avg_data = [
            avg_stats["participation_score"],
            avg_stats["legislation_score"],
            avg_stats["speech_score"],
            avg_stats["voting_score"],
            avg_stats["cooperation_score"]
        ]
        
        datasets.append({
            "label": "전체 평균",
            "data": avg_data,
            "backgroundColor": "rgba(153, 102, 255, 0.6)",
            "borderColor": "rgba(153, 102, 255, 1)",
            "borderWidth": 1
        })
    
    # 차트 데이터 딕셔너리 구성
    chart_data = {
        "labels": labels,
        "datasets": datasets
    }
    
    return chart_data

def generate_keyword_chart_data(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    키워드 데이터를 차트 데이터로 변환
    
    Args:
        keywords: 키워드 목록
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(키워드) 추출
    labels = [keyword["keyword"] for keyword in keywords]
    
    # 데이터값(횟수) 추출
    counts = [keyword["count"] for keyword in keywords]
    
    # 색상 목록 생성
    colors = [
        'rgba(75, 192, 192, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(199, 199, 199, 0.6)',
        'rgba(83, 102, 255, 0.6)',
        'rgba(40, 159, 64, 0.6)',
        'rgba(210, 99, 132, 0.6)'
    ]
    
    # 색상 목록 생성 (테두리)
    border_colors = [color.replace('0.6', '1') for color in colors]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "발언 횟수",
            "data": counts,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors[:len(labels)],
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_speech_chart_data(speeches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    회의 구분별 발언 데이터를 차트 데이터로 변환
    
    Args:
        speeches: 회의 구분별 발언 목록
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(회의 구분) 추출
    labels = [speech["meeting_type"] for speech in speeches]
    
    # 데이터값(횟수) 추출
    counts = [speech["count"] for speech in speeches]
    
    # 색상 목록 생성
    colors = [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(199, 199, 199, 0.6)',
        'rgba(83, 102, 255, 0.6)'
    ]
    
    # 색상 목록 생성 (테두리)
    border_colors = [color.replace('0.6', '1') for color in colors]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "발언 횟수",
            "data": counts,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors[:len(labels)],
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_ranking_chart_data(top: List[Dict[str, Any]], bottom: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 상위/하위 의원 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 홈 ###
def generate_party_asset_chart_data(party_stats: Dict[str, Any]) -> Dict[str, Any]:
    # 정당별 평균 재산 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_term_score_chart_data(term_stats: Dict[str, Any]) -> Dict[str, Any]:
    # 초선/재선별 평균 점수 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 정당 ###
def generate_party_scores_chart_data(party_scores: Dict[str, Any]) -> Dict[str, Any]:
    # 정당별 평균 종합점수 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_party_bills_chart_data(party_bills: Dict[str, Any]) -> Dict[str, Any]:
    # 정당별 평균 대표발의안수 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 위원회 ###
def generate_committee_processing_chart_data(ratios: Dict[str, Any]) -> Dict[str, Any]:
    # 위원회별 접수/처리 비율 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_committee_scores_chart_data(scores: Dict[str, Any]) -> Dict[str, Any]:
    # 위원회별 평균 종합점수 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 초선/재선+ ###
def generate_term_tier_chart_data(term_tier_data: Dict[str, Any]) -> Dict[str, Any]:
    # 초선/재선별 티어 분포 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_term_asset_chart_data(term_asset_data: Dict[str, Any]) -> Dict[str, Any]:
    # 초선/재선별 평균 재산 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 성별 ###
def generate_gender_tier_chart_data(gender_tier_data: Dict[str, Any]) -> Dict[str, Any]:
    # 성별 티어 분포 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_gender_asset_chart_data(gender_asset_data: Dict[str, Any]) -> Dict[str, Any]:
    # 성별 평균 재산 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 나이별 ###
def generate_age_score_chart_data(age_score_data: Dict[str, Any]) -> Dict[str, Any]:
    # 나이대별 평균 종합점수 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_age_asset_chart_data(age_asset_data: Dict[str, Any]) -> Dict[str, Any]:
    # 나이대별 평균 재산 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

### 잡다한 랭킹 - 재산 ###
def generate_score_asset_correlation_chart_data(correlation_data: Dict[str, Any]) -> Dict[str, Any]:
    # 활동점수와 재산 상관관계 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass

def generate_party_asset_ratio_chart_data(party_asset_data: Dict[str, Any]) -> Dict[str, Any]:
    # 정당별 재산 비율 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    pass