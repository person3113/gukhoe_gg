import requests
import xmltodict
from typing import List, Dict, Any, Optional

from app.config import settings
from app.utils.xml_parser import parse_xml_to_dict

class ApiService:
    def __init__(self, api_key=None):
        # API 키 설정 및 기본 URL 초기화
        self.api_key = api_key or settings.API_KEY
        self.base_url = settings.BASE_API_URL
        self.endpoints = settings.API_ENDPOINTS
        self.default_args = settings.DEFAULT_API_ARGS
        self.required_args = settings.API_REQUIRED_ARGS
    
    async def _make_api_call(self, endpoint_key: str, additional_params: Optional[Dict[str, str]] = None) -> str:
      """
      공통 API 호출 메서드
      
      Args:
          endpoint_key: API 엔드포인트 키 (config에 정의된 키)
          additional_params: 추가 요청 인자
              
      Returns:
          str: API 응답 (XML 문자열)
      """
      # 1. 엔드포인트 URL 구성 (base_url + endpoint)
      
      # 2. 기본 인자 설정 (Key, Type, pIndex, pSize)
      
      # 3. API별 필수 인자 확인 및 추가
      
      # 4. 추가 인자 병합
      
      # 5. API 호출 및 응답 받기
      
      # 6. 응답 반환 (XML 문자열)
      
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

    async def fetch_legislator_images(self) -> List[Dict[str, Any]]:
        """
        국회의원 사진 정보 API 호출
        
        Returns:
            List[Dict[str, Any]]: 의원 사진 정보 리스트
        """
        # 호출: self._make_api_call("legislator_integrated")로 국회의원 정보 통합 API 호출
        # 호출: parse_xml_to_dict()로 XML 응답 파싱
        # 국회의원코드(NAAS_CD)와 사진 URL(NAAS_PIC) 추출
        # 결과 리스트 구성: [{"mona_cd": "...", "profile_image_url": "..."}]
        # 반환: 사진 정보 리스트
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