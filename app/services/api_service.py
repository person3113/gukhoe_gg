import requests
import xmltodict
from typing import List, Dict, Any, Optional

from app.config import settings
from app.utils.xml_parser import parse_xml_to_dict

class ApiService:
    def __init__(self, api_key: Optional[str] = None):
        # API 키 설정 및 기본 URL 초기화
        self.api_key = api_key or settings.API_KEY
        self.base_url = settings.BASE_API_URL
        pass

    async def fetch_legislators_info(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 인적사항 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 의원 정보 리스트
        pass

    async def fetch_legislators_sns(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 SNS정보 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 의원 SNS 정보 리스트
        pass

    async def fetch_committee_members(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 위원회 위원 명단 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회 멤버십 정보 리스트
        pass

    async def fetch_bills(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 발의법률안 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 법안 정보 리스트
        pass

    async def fetch_vote_results(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 본회의 표결정보 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 표결 결과 리스트
        pass