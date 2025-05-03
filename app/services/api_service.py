import requests
import xmltodict
from typing import List, Dict, Any, Optional

from app.config import settings
from app.utils.xml_parser import parse_xml_to_dict

class ApiService:
    def __init__(self, api_key=None):
        # API 키 설정 및 기본 URL 초기화
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
        
    async def fetch_committee_info(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 위원회 현황 정보 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회 정보 리스트 (위원회명, 현원, 위원정수, 위원장 등)
        pass

    async def fetch_bills(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 발의법률안 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 법안 정보 리스트
        pass
        
    async def fetch_processed_bills_stats(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 처리 의안통계(위원회별) API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회별 처리 의안 통계 리스트 (위원회명, 접수건수, 처리건수, 보류건수)
        pass

    async def fetch_processed_bill_ids(self, age='22') -> List[str]:
        # 1. "법률안 심사 및 처리(처리의안)" API 호출
        # 2. "본회의 처리안건_법률안" API 호출
        # 3. 두 API에서 얻은 BILL_ID 추출
        # 4. 중복 제거를 위해 집합(set)으로 변환 후 다시 리스트로
        # 반환: 중복 제거된 처리된 법률안 ID 목록
        pass

    async def fetch_vote_results(self, legislator_id=None, age='22') -> List[Dict[str, Any]]:
        # 호출: self.fetch_processed_bill_ids()로 처리된 법안 ID 목록 가져오기
        # 각 법안 ID에 대해 본회의 표결 찬반 목록 API 호출
        # 특정 의원 ID가 제공되면 해당 의원의 표결 결과만 필터링
        # 반환: 표결 결과 리스트
        pass