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
    # Total을 제외한 실제 회의유형 데이터만 필터링
    filtered_speeches = [speech for speech in speeches if speech["meeting_type"] != "Total"]

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

def generate_ranking_chart_data(top_legislators: list, bottom_legislators: list, category: str = 'overall') -> dict:
    # 상위/하위 의원 데이터를 차트 데이터로 변환
    # 반환: 차트 데이터 딕셔너리
    """

    기존에 변수 이름이 이거였는데 오류나서 바꿈.    
    Args:
        top_legislators: 상위 의원 리스트
        bottom_legislators: 하위 의원 리스트
    
    """
    # 선택한 카테고리에 따라 점수 필드 결정
    if category == 'participation':
        score_field = 'participation_score'
        score_label = '참여 점수'
    elif category == 'legislation':
        score_field = 'legislation_score'
        score_label = '입법활동 점수'
    elif category == 'speech':
        score_field = 'speech_score'
        score_label = '의정발언 점수'
    elif category == 'voting':
        score_field = 'voting_score'
        score_label = '표결 책임성 점수'
    elif category == 'cooperation':
        score_field = 'cooperation_score'
        score_label = '협치/초당적 활동 점수'
    else:  # 'overall'
        score_field = 'overall_score'
        score_label = '종합 점수'
    
    # 상위 의원 이름과 점수
    top_names = [leg["name"] for leg in top_legislators]
    top_scores = [leg[score_field] for leg in top_legislators]
    
    # 하위 의원 이름과 점수
    bottom_names = [leg["name"] for leg in bottom_legislators]
    bottom_scores = [leg[score_field] for leg in bottom_legislators]
    # 차트 데이터 구성
    chart_data = {
        "top": {
            "labels": top_names,
            "datasets": [{
                "label": score_label,
                "data": top_scores,
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1
            }]
        },
        "bottom": {
            "labels": bottom_names,
            "datasets": [{
                "label": score_label,
                "data": bottom_scores,
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1
            }]
        }
    }
    
    return chart_data

### 잡다한 랭킹 - 홈 ###
def generate_party_asset_chart_data(party_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    정당별 평균 재산 데이터를 차트 데이터로 변환
    
    Args:
        party_stats: 정당별 평균 재산 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(정당명) 추출
    labels = list(party_stats.keys())
    
    # 데이터값(평균 재산) 추출
    values = [party_stats[party] for party in labels]
    
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
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 재산 (억원)",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_term_score_chart_data(term_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    초선/재선별 평균 점수 데이터를 차트 데이터로 변환
    
    Args:
        term_stats: 초선/재선별 평균 점수 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(선수) 추출
    labels = list(term_stats.keys())
    
    # 데이터값(평균 점수) 추출
    values = [term_stats[term] for term in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 종합점수",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 정당 ###

def generate_party_scores_chart_data(party_scores: Dict[str, float]) -> Dict[str, Any]:
    """
    정당별 평균 종합점수 데이터를 차트 데이터로 변환
    
    Args:
        party_scores: 정당별 평균 종합점수 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(정당명) 추출
    labels = list(party_scores.keys())
    
    # 데이터값(평균 점수) 추출
    scores = [party_scores[party] for party in labels]
    
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
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 종합점수",
            "data": scores,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_party_bills_chart_data(party_bills: Dict[str, float]) -> Dict[str, Any]:
    """
    정당별 평균 대표발의안수 데이터를 차트 데이터로 변환
    
    Args:
        party_bills: 정당별 평균 대표발의안수 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(정당명) 추출
    labels = list(party_bills.keys())
    
    # 데이터값(평균 발의안수) 추출
    counts = [party_bills[party] for party in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(199, 199, 199, 0.6)',
        'rgba(83, 102, 255, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 대표발의안수",
            "data": counts,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 위원회 ###
def generate_committee_processing_chart_data(ratios: Dict[str, Any]) -> Dict[str, Any]:
    """
    위원회별 법안 처리 비율 데이터를 차트 데이터로 변환
    
    Args:
        ratios: 위원회별 처리 비율 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(위원회명) 추출
    labels = list(ratios.keys())
    
    # 데이터값(처리 비율) 추출
    values = [ratios[committee]['ratio'] for committee in labels]
    
    # 색상 목록 생성 (처리 비율에 따라 색상 변경)
    colors = []
    for committee in labels:
        ratio = ratios[committee]['ratio']
        if ratio >= 80:
            colors.append('rgba(75, 192, 192, 0.6)')  # 높은 비율: 초록색
        elif ratio >= 50:
            colors.append('rgba(255, 206, 86, 0.6)')  # 중간 비율: 노란색
        else:
            colors.append('rgba(255, 99, 132, 0.6)')  # 낮은 비율: 빨간색
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "처리 비율 (%)",
            "data": values,
            "backgroundColor": colors,
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_committee_scores_chart_data(scores: Dict[str, float]) -> Dict[str, Any]:
    """
    위원회별 평균 종합점수 데이터를 차트 데이터로 변환
    
    Args:
        scores: 위원회별 평균 종합점수 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(위원회명) 추출
    labels = list(scores.keys())
    
    # 데이터값(평균 종합점수) 추출
    values = [scores[committee] for committee in labels]
    
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
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 종합점수",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 초선/재선+ ###
def generate_term_tier_chart_data(term_tier_data: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    초선/재선별 티어 분포 데이터를 차트 데이터로 변환
    
    Args:
        term_tier_data: 초선/재선별 티어 분포 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(선수) 추출
    labels = list(term_tier_data.keys())
    
    # 티어 목록 (모든 가능한 티어)
    all_tiers = ["Challenger", "Master", "Diamond", "Platinum", "Gold", "Silver", "Bronze", "Iron"]
    
    # 티어별 색상 매핑
    tier_colors = {
        "Challenger": 'rgba(255, 0, 0, 0.6)',       # 빨강
        "Master": 'rgba(255, 165, 0, 0.6)',         # 주황
        "Diamond": 'rgba(0, 191, 255, 0.6)',        # 하늘
        "Platinum": 'rgba(50, 205, 50, 0.6)',       # 연두
        "Gold": 'rgba(255, 215, 0, 0.6)',           # 금색
        "Silver": 'rgba(192, 192, 192, 0.6)',       # 은색
        "Bronze": 'rgba(205, 127, 50, 0.6)',        # 동색
        "Iron": 'rgba(169, 169, 169, 0.6)'          # 회색
    }
    
    # 데이터셋 생성
    datasets = []
    for tier in all_tiers:
        # 해당 티어의 데이터 추출
        data = []
        for term in labels:
            term_data = term_tier_data.get(term, {})
            data.append(term_data.get(tier, 0))
        
        # 데이터가 모두 0인 경우 스킵
        if sum(data) == 0:
            continue
        
        # 데이터셋 추가
        datasets.append({
            "label": tier,
            "data": data,
            "backgroundColor": tier_colors.get(tier, 'rgba(200, 200, 200, 0.6)'),
            "borderColor": tier_colors.get(tier, 'rgba(200, 200, 200, 1)').replace('0.6', '1'),
            "borderWidth": 1
        })
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": datasets
    }
    
    return chart_data

def generate_term_asset_chart_data(term_asset_data: Dict[str, float]) -> Dict[str, Any]:
    """
    초선/재선별 평균 재산 데이터를 차트 데이터로 변환
    
    Args:
        term_asset_data: 초선/재선별 평균 재산 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(선수) 추출
    labels = list(term_asset_data.keys())
    
    # 데이터값(평균 재산) 추출
    values = [term_asset_data[term] for term in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(153, 102, 255, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 재산 (억원)",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 성별 ###
### 잡다한 랭킹 - 성별 ###
def generate_gender_tier_chart_data(gender_tier_data: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    성별 티어 분포 데이터를 차트 데이터로 변환
    
    Args:
        gender_tier_data: 성별 티어 분포 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(성별) 추출
    labels = list(gender_tier_data.keys())
    
    # 티어 목록 (모든 가능한 티어)
    all_tiers = ["Challenger", "Master", "Diamond", "Platinum", "Gold", "Silver", "Bronze", "Iron"]
    
    # 티어별 색상 매핑
    tier_colors = {
        "Challenger": 'rgba(255, 0, 0, 0.6)',       # 빨강
        "Master": 'rgba(255, 165, 0, 0.6)',         # 주황
        "Diamond": 'rgba(0, 191, 255, 0.6)',        # 하늘
        "Platinum": 'rgba(50, 205, 50, 0.6)',       # 연두
        "Gold": 'rgba(255, 215, 0, 0.6)',           # 금색
        "Silver": 'rgba(192, 192, 192, 0.6)',       # 은색
        "Bronze": 'rgba(205, 127, 50, 0.6)',        # 동색
        "Iron": 'rgba(169, 169, 169, 0.6)'          # 회색
    }
    
    # 데이터셋 생성
    datasets = []
    for tier in all_tiers:
        # 해당 티어의 데이터 추출
        data = []
        for gender in labels:
            gender_data = gender_tier_data.get(gender, {})
            data.append(gender_data.get(tier, 0))
        
        # 데이터가 모두 0인 경우 스킵
        if sum(data) == 0:
            continue
        
        # 데이터셋 추가
        datasets.append({
            "label": tier,
            "data": data,
            "backgroundColor": tier_colors.get(tier, 'rgba(200, 200, 200, 0.6)'),
            "borderColor": tier_colors.get(tier, 'rgba(200, 200, 200, 1)').replace('0.6', '1'),
            "borderWidth": 1
        })
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": datasets
    }
    
    return chart_data

def generate_gender_asset_chart_data(gender_asset_data: Dict[str, float]) -> Dict[str, Any]:
    """
    성별 평균 재산 데이터를 차트 데이터로 변환
    
    Args:
        gender_asset_data: 성별 평균 재산 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(성별) 추출
    labels = list(gender_asset_data.keys())
    
    # 데이터값(평균 재산) 추출
    values = [gender_asset_data[gender] for gender in labels]
    
    # 색상 목록 생성 (성별에 따라 다른 색상 사용)
    colors = []
    for gender in labels:
        if gender == "남":
            colors.append('rgba(54, 162, 235, 0.6)')  # 파란색
        else:
            colors.append('rgba(255, 99, 132, 0.6)')  # 분홍색
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 재산 (억원)",
            "data": values,
            "backgroundColor": colors,
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 나이별 ###
def generate_age_score_chart_data(age_score_data: Dict[str, float]) -> Dict[str, Any]:
    """
    나이대별 평균 종합점수 데이터를 차트 데이터로 변환
    
    Args:
        age_score_data: 나이대별 평균 종합점수 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(나이대) 추출
    labels = list(age_score_data.keys())
    
    # 데이터값(평균 점수) 추출
    values = [age_score_data[age] for age in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 종합점수",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_age_asset_chart_data(age_asset_data: Dict[str, float]) -> Dict[str, Any]:
    """
    나이대별 평균 재산 데이터를 차트 데이터로 변환
    
    Args:
        age_asset_data: 나이대별 평균 재산 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(나이대) 추출
    labels = list(age_asset_data.keys())
    
    # 데이터값(평균 재산) 추출
    values = [age_asset_data[age] for age in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 206, 86, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "평균 재산 (억원)",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

### 잡다한 랭킹 - 재산 ###
def generate_score_asset_correlation_chart_data(correlation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    활동점수와 재산 상관관계 데이터를 차트 데이터로 변환
    
    Args:
        correlation_data: 점수-재산 상관관계 데이터
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 데이터 포인트들 추출
    data_points = correlation_data.get("data_points", [])
    
    # 산점도 차트 데이터 구성
    chart_data = {
        "datasets": [{
            "label": "의원별 점수-재산 분포",
            "data": [
                {"x": point["score"], "y": point["asset"], "r": 5, "name": point["name"]}
                for point in data_points
            ],
            "backgroundColor": 'rgba(75, 192, 192, 0.6)',
            "borderColor": 'rgba(75, 192, 192, 1)',
            "borderWidth": 1
        }]
    }
    
    return chart_data

def generate_party_asset_ratio_chart_data(party_asset_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    정당별 재산 비율 데이터를 차트 데이터로 변환
    
    Args:
        party_asset_data: 정당별 재산 비율 딕셔너리
        
    Returns:
        차트 데이터 딕셔너리
    """
    # 차트에 표시할 라벨(정당명) 추출
    labels = list(party_asset_data.keys())
    
    # 데이터값(재산 비율) 추출
    values = [party_asset_data[party]["ratio"] for party in labels]
    
    # 색상 목록 생성
    colors = [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)'
    ]
    
    # 색상이 부족한 경우 반복 사용
    if len(labels) > len(colors):
        colors = colors * (len(labels) // len(colors) + 1)
    
    # 테두리 색상 생성
    border_colors = [color.replace('0.6', '1') for color in colors[:len(labels)]]
    
    # 차트 데이터 구성
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "재산 비율 (%)",
            "data": values,
            "backgroundColor": colors[:len(labels)],
            "borderColor": border_colors,
            "borderWidth": 1
        }]
    }
    
    return chart_data

