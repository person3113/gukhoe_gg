import requests
from bs4 import BeautifulSoup
import urllib.parse

# 먼저 모든 모델을 명시적으로 임포트하여 순환 참조 문제 해결
from app.models.legislator import Legislator
from app.models.sns import LegislatorSNS
from app.models.committee import Committee, CommitteeHistory, CommitteeMember
from app.models.speech import SpeechKeyword, SpeechByMeeting
from app.models.attendance import Attendance
from app.models.bill import Bill, BillCoProposer
from app.models.vote import Vote, VoteResult

def parse_speech_count_from_nanet(legislator_name: str) -> int:
    """
    국회회의록 빅데이터 사이트에서 의원의 발언 횟수를 파싱하는 함수
    
    Args:
        legislator_name: 국회의원 이름
    
    Returns:
        int: 발언 횟수 (실패 시 0 반환)
    """
    try:
        # 의원 이름 URL 인코딩
        encoded_name = urllib.parse.quote(legislator_name)
        
        # URL 구성 - 22대 국회 필터링
        url = f"https://dataset.nanet.go.kr/list?srchQ=&srchQList%5B0%5D.srchKey=&srchQList%5B0%5D.srchGb=total&srchQList%5B0%5D.srchIdx=total&srchQList%5B0%5D.srchQ={encoded_name}&srchQList%5B0%5D.srchDisp={encoded_name}&srchQList%5B0%5D.srchCond=AND&orgId=NAM&_orgId=NAM&sort=score%3Adesc&srchGb=total&srchIdx=&searchType=+&srchCond=&srchDisp={encoded_name}&chkReSrchQ=N&recordCountPerPage=10&pageNo=1&phraseSearch=&phraseField=&searchWord=&tabGb=speaker&menuGb=list&speaker=&speakerId=&conferNum=&facetOrgSubId=&facetDaeNum=22&facetClassCode=&facetCommName=&facetCommSubName=&facetMeetingYear=&facetFrequency=&facetMemberName=&dtl_orgId=&dtl_orgSubId=&dtl_daeNums=&dtl_classCode=&dtl_subClassCode=&dtl_commNames=&dtl_startFrequency=&dtl_endFrequency=&dtl_startMeetingDate=&dtl_endMeetingDate="
        
        # 웹 페이지 요청
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 숫자 문자열을 정수로 변환하는 함수
            def extract_number(text):
                if not text:
                    return 0
                # 쉼표와 공백 제거하고 숫자만 추출
                import re
                number_str = re.sub(r'[^\d]', '', text.strip())
                if number_str:
                    return int(number_str)
                return 0
            
            # 제22대 슬라이드 찾기 (swiper-slide-s22)
            slide_22 = soup.find('div', class_='swiper-slide-s22')
            if slide_22:
                # 슬라이드 내에서 swiper_txt pb-3 클래스를 가진 div 찾기
                count_div = slide_22.find('div', class_='swiper_txt pb-3')
                if count_div:
                    return extract_number(count_div.text)
            
            return 0
        else:
            print(f"HTTP 오류: {response.status_code} - {legislator_name}")
            return 0
            
    except Exception as e:
        print(f"발언 횟수 파싱 중 오류 발생: {str(e)} - {legislator_name}")
        return 0