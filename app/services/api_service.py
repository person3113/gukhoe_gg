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
            print("API 호출 시작: legislator_sns")
            
            # 결과 리스트 초기화
            all_sns_info = []
            
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
                
                print(f"SNS 정보 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("legislator_sns", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'negnlnyvatsjwocar' 구조 처리 (SNS 정보 API의 응답 구조)
                if 'negnlnyvatsjwocar' in data_dict:
                    root = data_dict['negnlnyvatsjwocar']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 SNS 정보 수: {total_count}")
                    
                    # 'row' 태그에서 SNS 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}개의 SNS 정보 추출")
                    
                    # SNS 정보 매핑
                    for item in items:
                        sns_info = {
                            "mona_cd": item.get("MONA_CD", ""),
                            "t_url": item.get("T_URL", ""),
                            "f_url": item.get("F_URL", ""),
                            "y_url": item.get("Y_URL", ""),
                            "b_url": item.get("B_URL", "")
                        }
                        all_sns_info.append(sns_info)
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and len(all_sns_info) >= total_count:
                        print(f"모든 SNS 데이터({total_count}개)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(negnlnyvatsjwocar)를 찾지 못했습니다.")
                    break
            
            print(f"최종 처리된 SNS 정보 수: {len(all_sns_info)}")
            return all_sns_info
            
        except Exception as e:
            print(f"국회의원 SNS 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_legislator_images(self, legislators_info: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        국회의원 사진 정보 API 호출 - 이미 수집된 의원 정보(mona_cd)를 활용하여 필요한 의원의 사진만 가져옴
        
        Args:
            legislators_info: 이미 수집된 의원 정보 목록 (None인 경우 내부에서 수집)
        
        Returns:
            List[Dict[str, Any]]: 의원 사진 정보 리스트
        """
        try:
            print("국회의원 사진 정보 수집 시작")
            
            # 의원 정보가 제공되지 않은 경우 내부에서 수집
            if not legislators_info:
                legislators_info = self.fetch_legislators_info()
                if not legislators_info:
                    print("의원 정보를 가져올 수 없습니다.")
                    return []
            
            # 결과 리스트 초기화
            all_image_info = []
            total_legislators = len(legislators_info)
            
            print(f"총 {total_legislators}명의 의원 사진 정보를 수집합니다.")
            
            # 각 의원별로 사진 정보 수집
            for index, legislator in enumerate(legislators_info):
                mona_cd = legislator.get('mona_cd', '')
                if not mona_cd:
                    continue
                
                # 진행 상황 로깅 (10명마다 출력)
                if index % 10 == 0:
                    print(f"의원 사진 정보 수집 중: {index+1}/{total_legislators} ({(index+1)/total_legislators*100:.1f}%)")
                
                # API 호출
                additional_params = {
                    "NAAS_CD": mona_cd
                }
                
                response_text = self._make_api_call("legislator_integrated", additional_params)
                
                if not response_text:
                    print(f"의원(ID: {mona_cd}) 사진 정보를 가져올 수 없습니다.")
                    continue
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류 (의원 ID: {mona_cd}): {data_dict.get('message')}")
                    continue
                
                # 'ALLNAMEMBER' 구조 처리
                if 'ALLNAMEMBER' in data_dict:
                    root = data_dict['ALLNAMEMBER']
                    
                    # 'row' 태그에서 사진 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 현재 의원의 사진 정보를 찾아 추가
                    for item in items:
                        if item.get("NAAS_CD") == mona_cd:
                            profile_image_url = item.get("NAAS_PIC", "")
                            if profile_image_url:
                                image_info = {
                                    "mona_cd": mona_cd,
                                    "profile_image_url": profile_image_url
                                }
                                all_image_info.append(image_info)
                                break
            
            print(f"최종 처리된 사진 정보 수: {len(all_image_info)}")
            return all_image_info
        
        except Exception as e:
            print(f"국회의원 사진 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_committee_members(self) -> List[Dict[str, Any]]:
        # 호출: requests.get()로 위원회 위원 명단 API 호출
        # 호출: utils.xml_parser.parse_xml_to_dict()로 XML 응답 파싱
        # 반환: 위원회 멤버십 정보 리스트
        pass
        
    def fetch_committee_info(self) -> List[Dict[str, Any]]:
        """
        위원회 현황 정보 API 호출
        
        Returns:
            List[Dict[str, Any]]: 위원회 정보 리스트
        """
        try:
            print("API 호출 시작: committee_info")
            
            # 결과 리스트 초기화
            all_committees = []
            
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
                
                print(f"위원회 현황 정보 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("committee_info", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'nxrvzonlafugpqjuh' 구조 처리 (위원회 현황 정보 API의 응답 구조)
                if 'nxrvzonlafugpqjuh' in data_dict:
                    root = data_dict['nxrvzonlafugpqjuh']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 위원회 수: {total_count}")
                    
                    # 'row' 태그에서 위원회 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}개의 위원회 정보 추출")
                    
                    # 위원회 정보 매핑
                    for item in items:
                        committee_info = {
                            "hr_dept_cd": item.get("HR_DEPT_CD", ""),  # 위원회 코드
                            "committee_name": item.get("COMMITTEE_NAME", ""),  # 위원회명
                            "cmt_div_nm": item.get("CMT_DIV_NM", ""),  # 위원회 구분
                            "hg_nm": item.get("HG_NM", ""),  # 위원장
                            "hg_nm_list": item.get("HG_NM_LIST", ""),  # 간사
                            "limit_cnt": item.get("LIMIT_CNT", ""),  # 위원정수
                            "curr_cnt": item.get("CURR_CNT", ""),  # 현원
                            "poly99_cnt": item.get("POLY99_CNT", ""),  # 비교섭단체위원수
                            "poly_cnt": item.get("POLY_CNT", "")  # 교섭단체위원수
                        }
                        all_committees.append(committee_info)
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and len(all_committees) >= total_count:
                        print(f"모든 위원회 데이터({total_count}개)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(nxrvzonlafugpqjuh)를 찾지 못했습니다.")
                    break
            
            print(f"최종 처리된 위원회 정보 수: {len(all_committees)}")
            return all_committees
            
        except Exception as e:
            print(f"위원회 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_committee_history(self) -> List[Dict[str, Any]]:
        """
        국회의원 위원회 경력 API 호출
        
        Returns:
            List[Dict[str, Any]]: 의원 위원회 경력 정보 리스트
        """
        try:
            print("API 호출 시작: committee_history")
            
            # 결과 리스트 초기화
            all_history = []
            
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
                
                print(f"위원회 경력 정보 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("committee_history", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'nyzrglyvagmrypezq' 구조 처리 (위원회 경력 API의 응답 구조)
                if 'nyzrglyvagmrypezq' in data_dict:
                    root = data_dict['nyzrglyvagmrypezq']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 위원회 경력 정보 수: {total_count}")
                    
                    # 'row' 태그에서 위원회 경력 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}개의 위원회 경력 정보 추출")
                    
                    # 위원회 경력 정보 매핑
                    for item in items:
                        history_info = {
                            "mona_cd": item.get("MONA_CD", ""),
                            "hg_nm": item.get("HG_NM", ""),
                            "frto_date": item.get("FRTO_DATE", ""),
                            "profile_sj": item.get("PROFILE_SJ", "")
                        }
                        all_history.append(history_info)
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and len(all_history) >= total_count:
                        print(f"모든 위원회 경력 데이터({total_count}개)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(nyzrglyvagmrypezq)를 찾지 못했습니다.")
                    break
            
            print(f"최종 처리된 위원회 경력 정보 수: {len(all_history)}")
            return all_history
            
        except Exception as e:
            print(f"위원회 경력 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_bills(self) -> List[Dict[str, Any]]:
        """
        국회의원 발의법률안 API 호출 - 새로운 발의안만 가져오도록 개선
        
        Returns:
            List[Dict[str, Any]]: 새로 추가된 법안 정보 리스트
        """
        try:
            from app.db.database import SessionLocal
            from app.models.bill import Bill
            
            db = SessionLocal()
            
            # 가장 최근 발의안의 제안일 확인
            latest_bill = db.query(Bill).order_by(Bill.propose_dt.desc()).first()
            latest_date = latest_bill.propose_dt if latest_bill else None
            
            print(f"최근 발의안 제안일: {latest_date}")
            
            # 결과 리스트 초기화
            all_bills = []
            new_bills = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보를 포함한 API 호출
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size),
                    "AGE": "22"  # 22대 국회 기준
                }
                
                print(f"법안 정보 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("bills", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'nzmimeepazxkubdpn' 구조 처리 (법안 정보 API의 응답 구조)
                if 'nzmimeepazxkubdpn' in data_dict:
                    root = data_dict['nzmimeepazxkubdpn']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 법안 수: {total_count}")
                    
                    # 'row' 태그에서 법안 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}개의 법안 정보 추출")
                    
                    # 법안 정보 매핑 및 기존 발의안 확인
                    found_all_existing = False
                    for item in items:
                        # 법안 정보 매핑
                        bill_info = {
                            "bill_id": item.get("BILL_ID", ""),
                            "bill_no": item.get("BILL_NO", ""),
                            "bill_name": item.get("BILL_NAME", ""),
                            "propose_dt": item.get("PROPOSE_DT", ""),
                            "detail_link": item.get("DETAIL_LINK", ""),
                            "proposer": item.get("PROPOSER", ""),
                            "committee": item.get("COMMITTEE", ""),
                            "proc_result": item.get("PROC_RESULT", ""),
                            "main_proposer": item.get("RST_PROPOSER", ""),
                            "co_proposers": item.get("PUBL_PROPOSER", ""),
                            "MEMBER_LIST": item.get("MEMBER_LIST", "")
                        }
                        
                        all_bills.append(bill_info)
                        
                        # 이미 DB에 있는 발의안인지 확인
                        bill_no = bill_info["bill_no"]
                        existing_bill = db.query(Bill).filter(Bill.bill_no == bill_no).first()
                        
                        if not existing_bill:
                            # DB에 없는 새로운 발의안
                            new_bills.append(bill_info)
                        else:
                            # 해당 제안일이 최신 제안일보다 이전이면, 모든 새 법안을 가져왔다고 가정
                            current_propose_dt = bill_info["propose_dt"]
                            if latest_date and current_propose_dt <= latest_date:
                                # 이미 존재하는 발의안이고 최신 발의안보다 이전이면 더 이상 조회 필요 없음
                                found_all_existing = True
                                print(f"이미 존재하는 발의안 발견: {bill_no}, 검색 종료")
                                break
                    
                    # 모든 기존 발의안을 찾았으면 종료
                    if found_all_existing:
                        break
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and len(all_bills) >= total_count:
                        print(f"모든 데이터({total_count}개)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(nzmimeepazxkubdpn)를 찾지 못했습니다.")
                    break
            
            db.close()
            
            print(f"전체 법안 수: {len(all_bills)}, 새로 추가된 법안 수: {len(new_bills)}")
            return new_bills
            
        except Exception as e:
            print(f"국회의원 법안 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
    def fetch_processed_bills_stats(self) -> List[Dict[str, Any]]:
        """
        처리 의안통계(위원회별) API 호출
        
        Returns:
            List[Dict[str, Any]]: 위원회별 처리 의안 통계 리스트
        """
        try:
            print("API 호출 시작: processed_bills_stats")
            
            # 결과 리스트 초기화
            all_stats = []
            
            # API 호출 파라미터 설정 - ERACO는 config에서 필수 인자로 지정됨
            additional_params = {}
            
            print("처리 의안통계 요청 중...")
            response_text = self._make_api_call("processed_bills_stats", additional_params)
            
            if not response_text:
                print("응답이 없습니다!")
                return []
            
            # XML 응답 파싱
            data_dict = parse_xml_to_dict(response_text)
            
            # 오류 체크
            if data_dict.get('error'):
                print(f"API 오류: {data_dict.get('message')}")
                return []
            
            # 'BILLCNTCMIT' 구조 처리 (처리 의안통계 API의 응답 구조)
            if 'BILLCNTCMIT' in data_dict:
                root = data_dict['BILLCNTCMIT']
                
                # 'row' 태그에서 통계 정보 추출
                items = root.get('row', [])
                
                # 단일 항목인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                
                # 데이터가 없는 경우
                if not items:
                    print("처리 의안통계 데이터가 없습니다.")
                    return []
                
                print(f"총 {len(items)}개의 위원회 통계 정보 추출")
                
                # 통계 정보 매핑
                for item in items:
                    stat_info = {
                        "cmit_nm": item.get("CMIT_NM", ""),
                        "rcp_cnt": item.get("RCP_CNT", "0"),
                        "proc_cnt": item.get("PROC_CNT", "0"),
                        "rsvt_cnt": item.get("RSVT_CNT", "0")
                    }
                    all_stats.append(stat_info)
            else:
                print("예상한 구조(BILLCNTCMIT)를 찾지 못했습니다.")
                return []
            
            print(f"처리 의안통계 수집 완료: {len(all_stats)}개 위원회")
            return all_stats
            
        except Exception as e:
            print(f"처리 의안통계 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_bills_with_votes(self, age='22') -> List[str]:
        """
        표결이 이루어진 법안 ID 목록 조회 (수정가결, 원안가결, 부결인 법안)
        
        Args:
            age: 국회 대수 (기본값: '22')
        
        Returns:
            표결이 이루어진 법안 ID 목록
        """
        try:
            from app.db.database import SessionLocal
            from app.models.bill import Bill
            from app.models.vote import Vote
            
            db = SessionLocal()
            
            # 가장 최근 표결 조회
            latest_vote = db.query(Vote).order_by(Vote.vote_date.desc()).first()
            latest_date = latest_vote.vote_date if latest_vote else None
            
            print(f"최근 표결일: {latest_date}")
            
            # 결과 리스트 초기화
            voted_bill_ids = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보를 포함한 API 호출
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size),
                    "AGE": age
                }
                
                print(f"법률안 심사 및 처리(의안검색) 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("tvbpmbill11", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # 'TVBPMBILL11' 구조 처리
                if 'TVBPMBILL11' in data_dict:
                    root = data_dict['TVBPMBILL11']
                    
                    # 첫 페이지에서만 총 개수 정보 확인
                    if total_count is None and 'head' in root:
                        head = root['head']
                        total_count = int(head.get('list_total_count', 0))
                        print(f"총 법안 수: {total_count}")
                    
                    # 'row' 태그에서 법안 정보 추출
                    items = root.get('row', [])
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # 페이지에 항목이 없으면 종료
                    if not items:
                        print(f"페이지 {page_index}에 항목이 없습니다. 종료합니다.")
                        break
                    
                    print(f"페이지 {page_index}에서 {len(items)}개의 법안 정보 추출")
                    
                    # 표결이 있는 법안만 필터링
                    found_all_existing = False
                    for item in items:
                        # 표결 결과 확인
                        proc_result = item.get("PROC_RESULT_CD", "")
                        proc_date = item.get("PROC_DT", "")
                        bill_id = item.get("BILL_ID", "")
                        
                        # 수정가결, 원안가결, 부결인 법안만 선택
                        if proc_result in ["수정가결", "원안가결", "부결"] and bill_id:
                            # 기존 표결 확인
                            if latest_date and proc_date <= latest_date:
                                # 이미 처리된 표결이면 스킵
                                found_all_existing = True
                                print(f"이미 처리된 표결 발견 (날짜: {proc_date}), 검색 종료")
                                break
                            
                            # 기존 법안 DB에 없는 경우, 법안 정보 추가
                            existing_bill = db.query(Bill).filter(Bill.bill_no == item.get("BILL_NO", "")).first()

                            if existing_bill:
                                # 기존 법안 정보 업데이트
                                existing_bill.bill_id = bill_id
                                existing_bill.proc_result = proc_result
                                # 필요한 다른 필드들 업데이트
                                bill = existing_bill
                            else:
                                # 법안 기본 정보 저장
                                bill = Bill(
                                    bill_id=bill_id,
                                    bill_no=item.get("BILL_NO", ""),
                                    bill_name=item.get("BILL_NAME", ""),
                                    law_title=item.get("BILL_NAME", ""),  # law_title이 없으면 bill_name 사용
                                    propose_dt=item.get("PROPOSE_DT", ""),
                                    detail_link=item.get("LINK_URL", ""),
                                    proposer=item.get("PROPOSER", ""),
                                    committee=item.get("CURR_COMMITTEE", ""),
                                    proc_result=proc_result,
                                    main_proposer_id=None  # 대표발의자 정보 없음
                                )
                                db.add(bill)
                                db.flush()
                            
                            # 표결이 있는 법안 ID 추가
                            voted_bill_ids.append(bill_id)
                    
                    # 모든 기존 표결을 찾았으면 종료
                    if found_all_existing:
                        break
                    
                    # 다음 페이지로 이동
                    page_index += 1
                    
                    # 모든 데이터를 가져왔는지 확인
                    if total_count and (page_index-1) * page_size >= total_count:
                        print(f"모든 데이터({total_count}개)를 가져왔습니다.")
                        break
                else:
                    print(f"예상한 구조(TVBPMBILL11)를 찾지 못했습니다.")
                    break
            
            db.commit()
            db.close()
            
            print(f"표결이 있는 법안 수: {len(voted_bill_ids)}")
            return voted_bill_ids
            
        except Exception as e:
            print(f"표결 법안 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_vote_results(self, bill_id: str) -> Dict[str, Any]:
        """
        특정 법안의 표결 결과 조회
        
        Args:
            bill_id: 법안 ID
        
        Returns:
            표결 정보 딕셔너리
        """
        try:
            # API 호출 파라미터 설정
            additional_params = {
                "BILL_ID": bill_id,
                "AGE": "22",  # 22대 국회
                "pSize": "300"  # 최대한 많은 표결 결과를 한번에 가져오기
            }
            
            print(f"법안 {bill_id}의 표결 정보 요청 중...")
            response_text = self._make_api_call("vote_results", additional_params)
            
            if not response_text:
                print(f"법안 {bill_id}의 표결 정보를 가져올 수 없습니다.")
                return None
            
            # XML 응답 파싱
            data_dict = parse_xml_to_dict(response_text)
            
            # 오류 체크
            if data_dict.get('error'):
                print(f"API 오류: {data_dict.get('message')}")
                return None
            
            # 'nojepdqqaweusdfbi' 구조 처리 (표결 정보 API의 응답 구조)
            if 'nojepdqqaweusdfbi' in data_dict:
                root = data_dict['nojepdqqaweusdfbi']
                
                # 'row' 태그에서 표결 정보 추출
                items = root.get('row', [])
                
                # 단일 항목인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                
                # 표결 결과 없으면 None 반환
                if not items:
                    print(f"법안 {bill_id}의 표결 결과가 없습니다.")
                    return None
                
                # 표결 기본 정보 (첫 번째 항목에서 추출)
                first_item = items[0]
                vote_date = first_item.get("VOTE_DATE", "")
                bill_name = first_item.get("BILL_NAME", "")
                committee = first_item.get("CURR_COMMITTEE", "")
                law_title = first_item.get("LAW_TITLE", "")
                
                # 의원별 표결 결과 추출
                vote_results = []
                for item in items:
                    vote_result = {
                        "legislator_name": item.get("HG_NM", ""),
                        "party": item.get("POLY_NM", ""),
                        "result": item.get("RESULT_VOTE_MOD", "")
                    }
                    vote_results.append(vote_result)
                
                print(f"법안 {bill_id}의 표결 결과 {len(vote_results)}건 추출 완료")
                
                # 결과 딕셔너리 구성
                vote_info = {
                    "bill_id": bill_id,
                    "vote_date": vote_date,
                    "bill_name": bill_name,
                    "committee": committee,
                    "law_title": law_title,
                    "results": vote_results
                }
                
                return vote_info
            else:
                print(f"예상한 구조(nojepdqqaweusdfbi)를 찾지 못했습니다.")
                return None
                
        except Exception as e:
            print(f"표결 결과 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None