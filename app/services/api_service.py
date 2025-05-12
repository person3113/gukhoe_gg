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
    
    def _make_api_call(self, endpoint_key: str, additional_params: Optional[Dict[str, str]] = None) -> str:
        """
        공통 API 호출 메서드
        
        Args:
            endpoint_key: API 엔드포인트 키 (config에 정의된 키)
            additional_params: 추가 요청 인자
                
        Returns:
            str: API 응답 (XML 문자열)
        """
        # 1. 엔드포인트 URL 구성
        endpoint = self.endpoints.get(endpoint_key)
        if not endpoint:
            raise ValueError(f"Invalid endpoint key: {endpoint_key}")
        
        url = f"{self.base_url}{endpoint}"
        
        # 2. 기본 인자 설정
        params = {
            "Key": self.api_key,
            **self.default_args
        }
        
        # 3. API별 필수 인자 확인 및 추가
        required_args = self.required_args.get(endpoint_key, {})
        for key, value in required_args.items():
            if value is not None:
                params[key] = value
        
        # 4. 추가 인자 병합
        if additional_params:
            params.update(additional_params)
        
        # 5. API 호출 및 응답 받기
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # HTTP 오류 발생시 예외 발생
            
            # 6. 응답 반환 (XML 문자열)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"API 호출 오류 ({endpoint_key}): {str(e)}")
            return ""

    def fetch_legislators_info(self) -> List[Dict[str, Any]]:
        """
        국회의원 인적사항 API 호출 - 페이징 처리 추가
        
        Returns:
            List[Dict[str, Any]]: 의원 정보 리스트
        """
        try:
            print("API 호출 시작: legislator_info")
            
            # 결과 리스트 초기화
            all_legislators = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보를 포함한 API 호출
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size)
                }
                
                print(f"페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("legislator_info", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'nwvrqwxyaytdsfvhu' 구조 처리
                if 'nwvrqwxyaytdsfvhu' in data_dict:
                    root = data_dict['nwvrqwxyaytdsfvhu']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 의원 수: {total_count}")
                    
                    # 'row' 태그에서 의원 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}명의 의원 정보 추출")
                    
                    # 의원 정보 매핑 (모델에 있는 필드만 포함)
                    for item in items:
                        legislator = {
                            "mona_cd": item.get("MONA_CD", ""),
                            "hg_nm": item.get("HG_NM", ""),
                            "eng_nm": item.get("ENG_NM", ""),
                            "bth_date": item.get("BTH_DATE", ""),
                            "job_res_nm": item.get("JOB_RES_NM", ""),
                            "poly_nm": item.get("POLY_NM", ""),
                            "orig_nm": item.get("ORIG_NM", ""),
                            "cmit_nm": item.get("CMIT_NM", ""),
                            "reele_gbn_nm": item.get("REELE_GBN_NM", ""),
                            "sex_gbn_nm": item.get("SEX_GBN_NM", ""),
                            "tel_no": item.get("TEL_NO", ""),
                            "e_mail": item.get("E_MAIL", ""),
                            "mem_title": item.get("MEM_TITLE", "")
                        }
                        all_legislators.append(legislator)
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and len(all_legislators) >= total_count:
                        print(f"모든 데이터({total_count}명)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(nwvrqwxyaytdsfvhu)를 찾지 못했습니다.")
                    break
            
            print(f"최종 처리된 의원 수: {len(all_legislators)}")
            return all_legislators
            
        except Exception as e:
            print(f"국회의원 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_legislators_sns(self) -> List[Dict[str, Any]]:
        """
        국회의원 SNS정보 API 호출
        
        Returns:
            List[Dict[str, Any]]: 의원 SNS 정보 리스트
        """
        try:
            # API 호출
            response_text = self._make_api_call("legislator_sns")
            if not response_text:
                return []
            
            # XML 응답 파싱
            data_dict = parse_xml_to_dict(response_text)
            
            # 응답에서 SNS 정보 추출
            items = data_dict.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            # 단일 항목인 경우 리스트로 변환
            if not isinstance(items, list):
                items = [items]
            
            # 결과 리스트 구성
            result = []
            for item in items:
                sns = {
                    "mona_cd": item.get("MONA_CD", ""),
                    "t_url": item.get("T_URL", ""),
                    "f_url": item.get("F_URL", ""),
                    "y_url": item.get("Y_URL", ""),
                    "b_url": item.get("B_URL", "")
                }
                result.append(sns)
            
            return result
        except Exception as e:
            print(f"국회의원 SNS 정보 가져오기 오류: {str(e)}")
            return []

    def fetch_legislator_images(self) -> List[Dict[str, Any]]:
        """
        국회의원 사진 정보 API 호출
        
        Returns:
            List[Dict[str, Any]]: 의원 사진 정보 리스트
        """
        try:
            # API 호출
            response_text = self._make_api_call("legislator_integrated")
            if not response_text:
                return []
            
            # XML 응답 파싱
            data_dict = parse_xml_to_dict(response_text)
            
            # 응답에서 의원 정보 추출
            items = data_dict.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            # 단일 항목인 경우 리스트로 변환
            if not isinstance(items, list):
                items = [items]
            
            # 결과 리스트 구성
            result = []
            for item in items:
                # 국회의원코드와 사진 URL만 추출
                image_info = {
                    "mona_cd": item.get("NAAS_CD", ""),  # 통합API는 NAAS_CD를 사용
                    "profile_image_url": item.get("NAAS_PIC", "")
                }
                # 사진 URL이 있는 경우만 결과에 추가
                if image_info["profile_image_url"]:
                    result.append(image_info)
            
            return result
        except Exception as e:
            print(f"국회의원 사진 정보 가져오기 오류: {str(e)}")
            return []

    def fetch_committee_members(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 위원회 위원 명단 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회 멤버십 정보 리스트
        pass
        
    def fetch_committee_info(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 위원회 현황 정보 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회 정보 리스트 (위원회명, 현원, 위원정수, 위원장 등)
        pass

    def fetch_bills(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 국회의원 발의법률안 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 법안 정보 리스트
        pass
        
    def fetch_processed_bills_stats(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 처리 의안통계(위원회별) API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회별 처리 의안 통계 리스트 (위원회명, 접수건수, 처리건수, 보류건수)
        pass

    def fetch_processed_bill_ids(self, age='22') -> List[str]:
        # 1. "법률안 심사 및 처리(처리의안)" API 호출
        # 2. "본회의 처리안건_법률안" API 호출
        # 3. 두 API에서 얻은 BILL_ID 추출
        # 4. 중복 제거를 위해 집합(set)으로 변환 후 다시 리스트로
        # 반환: 중복 제거된 처리된 법률안 ID 목록
        pass

    def fetch_vote_results(self, legislator_id=None, age='22') -> List[Dict[str, Any]]:
        # 호출: self.fetch_processed_bill_ids()로 처리된 법안 ID 목록 가져오기
        # 각 법안 ID에 대해 본회의 표결 찬반 목록 API 호출
        # 특정 의원 ID가 제공되면 해당 의원의 표결 결과만 필터링
        # 반환: 표결 결과 리스트
        pass