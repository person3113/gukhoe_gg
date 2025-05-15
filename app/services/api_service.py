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
        """
        위원회 위원 명단 API 호출
        
        Returns:
            List[Dict[str, Any]]: 위원회 멤버십 정보 리스트
        """
        try:
            print("API 호출 시작: committee_members")
            
            # 결과 리스트 초기화
            all_committee_members = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보를 포함한 API 호출 (AGE 파라미터 필수)
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size),
                    "AGE": "22"  # 22대 국회 - 위원회 위원 명단 API에 필수
                }
                
                print(f"위원회 멤버 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("committee_members", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # OpenAPI_ServiceResponse 구조 처리
                root = None
                if 'OpenAPI_ServiceResponse' in data_dict:
                    service_response = data_dict['OpenAPI_ServiceResponse']
                    
                    # 응답 헤더 확인
                    if 'cmmMsgHeader' in service_response:
                        header = service_response['cmmMsgHeader']
                        if header.get('returnReasonCode') != '00':
                            print(f"API 처리 오류: {header.get('errMsg', '알 수 없는 오류')}")
                            break
                    
                    # 위원회 멤버 데이터 구조 확인
                    if 'nktulghcadyhmiqxi' in service_response:
                        root = service_response['nktulghcadyhmiqxi']
                    else:
                        print(f"데이터 구조를 찾을 수 없습니다. 키: {list(service_response.keys())}")
                        break
                else:
                    print(f"OpenAPI_ServiceResponse를 찾을 수 없습니다. 키: {list(data_dict.keys())}")
                    break
                
                # head 정보에서 총 개수 확인
                if 'head' in root and total_count is None:
                    head = root['head']
                    total_count = int(head.get('list_total_count', 0))
                    print(f"총 위원회 멤버 수: {total_count}")
                    
                    # 결과가 없는 경우 종료
                    if total_count == 0:
                        print("위원회 멤버 정보가 없습니다.")
                        break
                
                # row 데이터 추출
                items = root.get('row', [])
                
                # 단일 항목인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                
                # 페이지에 항목이 없으면 종료
                if not items:
                    print(f"페이지 {page_index}에 데이터가 없습니다. 종료합니다.")
                    break
                
                print(f"페이지 {page_index}에서 {len(items)}개의 위원회 멤버 정보 추출")
                
                # 위원회 멤버 정보 매핑
                for item in items:
                    member_info = {
                        "committee_name": item.get("DEPT_NM", ""),  # 위원회명
                        "member_name": item.get("HG_NM", ""),      # 의원명  
                        "member_code": item.get("MONA_CD", ""),    # 의원코드
                        "party_name": item.get("POLY_NM", ""),     # 정당명
                        "role": item.get("ROLE", ""),              # 역할
                        "start_date": item.get("START_DT", ""),    # 시작일
                        "end_date": item.get("END_DT", "")         # 종료일
                    }
                    all_committee_members.append(member_info)
                
                # 다음 페이지로 이동
                page_index += 1
                
                # 모든 데이터를 가져왔는지 확인
                if total_count and len(all_committee_members) >= total_count:
                    print(f"모든 데이터({total_count}개)를 가져왔습니다.")
                    break
                    
                # 예외적으로 너무 많은 페이지를 요청하는 것을 방지
                if page_index > 100:
                    print("페이지 수가 100을 초과했습니다. 종료합니다.")
                    break
            
            print(f"최종 처리된 위원회 멤버 수: {len(all_committee_members)}")
            return all_committee_members
            
        except Exception as e:
            print(f"위원회 멤버 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_committee_info(self) -> List[Dict[str, Any]]:
        """
        위원회 현황 정보 API 호출
        
        Returns:
            List[Dict[str, Any]]: 위원회 정보 리스트 (위원회명, 현원, 위원정수, 위원장 등)
        """
        try:
            print("API 호출 시작: committee_info")
            
            # 결과 리스트 초기화
            all_committee_info = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보를 포함한 API 호출 (AGE 파라미터 필수)
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size),
                    "AGE": "22"  # 22대 국회 - 위원회 현황 정보 API에 필수
                }
                
                print(f"위원회 정보 페이지 {page_index} 요청 중...")
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
                
                # OpenAPI_ServiceResponse 구조 처리
                root = None
                if 'OpenAPI_ServiceResponse' in data_dict:
                    service_response = data_dict['OpenAPI_ServiceResponse']
                    
                    # 응답 헤더 확인
                    if 'cmmMsgHeader' in service_response:
                        header = service_response['cmmMsgHeader']
                        if header.get('returnReasonCode') != '00':
                            print(f"API 처리 오류: {header.get('errMsg', '알 수 없는 오류')}")
                            break
                    
                    # 위원회 정보 데이터 구조 확인
                    if 'nxrvzonlafugpqjuh' in service_response:
                        root = service_response['nxrvzonlafugpqjuh']
                    else:
                        print(f"데이터 구조를 찾을 수 없습니다. 키: {list(service_response.keys())}")
                        break
                else:
                    print(f"OpenAPI_ServiceResponse를 찾을 수 없습니다. 키: {list(data_dict.keys())}")
                    break
                
                # head 정보에서 총 개수 확인
                if 'head' in root and total_count is None:
                    head = root['head']
                    total_count = int(head.get('list_total_count', 0))
                    print(f"총 위원회 수: {total_count}")
                    
                    # 결과가 없는 경우 종료
                    if total_count == 0:
                        print("위원회 정보가 없습니다.")
                        break
                
                # row 데이터 추출
                items = root.get('row', [])
                
                # 단일 항목인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                
                # 페이지에 항목이 없으면 종료
                if not items:
                    print(f"페이지 {page_index}에 데이터가 없습니다. 종료합니다.")
                    break
                
                print(f"페이지 {page_index}에서 {len(items)}개의 위원회 정보 추출")
                
                # 위원회 정보 매핑
                for item in items:
                    try:
                        committee_info = {
                            "committee_name": item.get("DEPT_NM", ""),                    # 위원회명
                            "committee_code": item.get("DEPT_CD", ""),                    # 위원회코드  
                            "current_count": int(item.get("CURR_CNT", 0) or 0),          # 현원
                            "limit_count": int(item.get("LIMIT_CNT", 0) or 0),           # 위원정수
                            "committee_chair": item.get("CMIT_CH", ""),                   # 위원장
                            "reception_count": int(item.get("RCP_CNT", 0) or 0),         # 접수건수
                            "processed_count": int(item.get("PROC_CNT", 0) or 0),        # 처리건수
                            "pending_count": int(item.get("PEND_CNT", 0) or 0),          # 보류건수
                            "start_date": item.get("START_DT", ""),                       # 활동시작일
                            "end_date": item.get("END_DT", "")                           # 활동종료일
                        }
                        all_committee_info.append(committee_info)
                    except (ValueError, TypeError) as e:
                        print(f"위원회 정보 파싱 오류: {e}, 항목: {item}")
                        continue
                
                # 다음 페이지로 이동
                page_index += 1
                
                # 모든 데이터를 가져왔는지 확인
                if total_count and len(all_committee_info) >= total_count:
                    print(f"모든 데이터({total_count}개)를 가져왔습니다.")
                    break
                    
                # 예외적으로 너무 많은 페이지를 요청하는 것을 방지
                if page_index > 100:
                    print("페이지 수가 100을 초과했습니다. 종료합니다.")
                    break
            
            print(f"최종 처리된 위원회 정보 수: {len(all_committee_info)}")
            return all_committee_info
            
        except Exception as e:
            print(f"위원회 정보 가져오기 오류: {str(e)}")
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
            List[Dict[str, Any]]: 위원회별 처리 의안 통계 리스트 (위원회명, 접수건수, 처리건수, 보류건수)
        """
        try:
            print("API 호출 시작: processed_bills_stats")
            
            # 결과 리스트 초기화
            all_bills_stats = []
            
            # 페이지 정보
            page_index = 1
            page_size = 100  # API 기본값
            total_count = None
            
            # 전체 데이터를 가져올 때까지 반복
            while True:
                # 페이지 정보 포함 (ERACO 파라미터는 required_args에서 자동 추가됨)
                additional_params = {
                    "pIndex": str(page_index),
                    "pSize": str(page_size)
                }
                
                print(f"의안통계 페이지 {page_index} 요청 중...")
                response_text = self._make_api_call("processed_bills_stats", additional_params)
                
                if not response_text:
                    print(f"페이지 {page_index} 응답이 없습니다!")
                    break
                
                # XML 응답 파싱
                data_dict = parse_xml_to_dict(response_text)
                
                # 오류 체크
                if data_dict.get('error'):
                    print(f"API 오류: {data_dict.get('message')}")
                    break
                
                # OpenAPI_ServiceResponse 구조 처리
                root = None
                if 'OpenAPI_ServiceResponse' in data_dict:
                    service_response = data_dict['OpenAPI_ServiceResponse']
                    
                    # 응답 헤더 확인
                    if 'cmmMsgHeader' in service_response:
                        header = service_response['cmmMsgHeader']
                        if header.get('returnReasonCode') != '00':
                            print(f"API 처리 오류: {header.get('errMsg', '알 수 없는 오류')}")
                            break
                    
                    # 의안통계 데이터 구조 확인
                    if 'BILLCNTCMIT' in service_response:
                        root = service_response['BILLCNTCMIT']
                    else:
                        print(f"데이터 구조를 찾을 수 없습니다. 키: {list(service_response.keys())}")
                        break
                else:
                    print(f"OpenAPI_ServiceResponse를 찾을 수 없습니다. 키: {list(data_dict.keys())}")
                    break
                
                # head 정보에서 총 개수 확인
                if 'head' in root and total_count is None:
                    head = root['head']
                    total_count = int(head.get('list_total_count', 0))
                    print(f"총 의안통계 수: {total_count}")
                    
                    # 결과가 없는 경우 종료
                    if total_count == 0:
                        print("의안통계 정보가 없습니다.")
                        break
                
                # row 데이터 추출
                items = root.get('row', [])
                
                # 단일 항목인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                
                # 페이지에 항목이 없으면 종료
                if not items:
                    print(f"페이지 {page_index}에 데이터가 없습니다. 종료합니다.")
                    break
                
                print(f"페이지 {page_index}에서 {len(items)}개의 의안통계 정보 추출")
                
                # 의안통계 정보 매핑
                for item in items:
                    try:
                        bills_stats = {
                            "committee_name": item.get("DEPT_NM", ""),                     # 위원회명
                            "reception_count": int(item.get("RCP_CNT", 0) or 0),          # 접수건수
                            "processed_count": int(item.get("PROC_CNT", 0) or 0),         # 처리건수  
                            "pending_count": int(item.get("PEND_CNT", 0) or 0),           # 보류건수
                            "progress_rate": float(item.get("PROG_RT", 0) or 0),          # 진행율(%)
                            "age": item.get("AGE", ""),                                    # 대수 정보
                            "session": item.get("SESS", "")                                # 회기 정보
                        }
                        all_bills_stats.append(bills_stats)
                    except (ValueError, TypeError) as e:
                        print(f"의안통계 정보 파싱 오류: {e}, 항목: {item}")
                        continue
                
                # 다음 페이지로 이동
                page_index += 1
                
                # 모든 데이터를 가져왔는지 확인
                if total_count and len(all_bills_stats) >= total_count:
                    print(f"모든 데이터({total_count}개)를 가져왔습니다.")
                    break
                    
                # 예외적으로 너무 많은 페이지를 요청하는 것을 방지
                if page_index > 100:
                    print("페이지 수가 100을 초과했습니다. 종료합니다.")
                    break
            
            print(f"최종 처리된 의안통계 수: {len(all_bills_stats)}")
            return all_bills_stats
            
        except Exception as e:
            print(f"의안통계 정보 가져오기 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_processed_bill_ids(self, age='22') -> List[str]:
        """
        처리된 법안 ID 목록 수집
        
        Args:
            age: 국회 대수 (기본값: '22')
        
        Returns:
            List[str]: 처리된 법안 ID 목록
        """
        # 1. "법률안 심사 및 처리(처리의안)" API 호출
        # 2. "본회의 처리안건_법률안" API 호출
        # 3. 두 API에서 얻은 BILL_ID 추출
        # 4. 중복 제거를 위해 집합(set)으로 변환 후 다시 리스트로
        # 반환: 중복 제거된 처리된 법률안 ID 목록
        # TODO: 구현 필요
        pass

    def fetch_vote_results(self, legislator_id=None, age='22') -> List[Dict[str, Any]]:
        """
        표결 결과 정보 수집
        
        Args:
            legislator_id: 특정 의원 ID (None인 경우 전체)
            age: 국회 대수 (기본값: '22')
        
        Returns:
            List[Dict[str, Any]]: 표결 결과 목록
        """
        # 호출: self.fetch_processed_bill_ids()로 처리된 법안 ID 목록 가져오기
        # 각 법안 ID에 대해 본회의 표결 찬반 목록 API 호출
        # 특정 의원 ID가 제공되면 해당 의원의 표결 결과만 필터링
        # 반환: 표결 결과 리스트
        # TODO: 구현 필요
        pass