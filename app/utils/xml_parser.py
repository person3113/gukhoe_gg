import xmltodict
from typing import Dict, Any, Optional

def parse_xml_to_dict(xml_string: str) -> Dict[str, Any]:
    """
    XML 문자열을 파이썬 딕셔너리로 변환
    
    Args:
        xml_string: XML 형식의 문자열
    
    Returns:
        Dict[str, Any]: 변환된 딕셔너리
    """
    try:
        # XML 문자열을 딕셔너리로 변환
        result = xmltodict.parse(xml_string)
        
        # 응답 오류 체크
        if 'response' in result:
            header = result['response'].get('header', {})
            result_code = header.get('resultCode')
            
            # 오류 코드 체크
            if result_code and result_code != '00' and result_code != '000':
                error_msg = header.get('resultMsg', '알 수 없는 오류')
                print(f"API 응답 오류: {error_msg} (코드: {result_code})")
                return {'error': True, 'message': error_msg, 'code': result_code}
        
        # 결과 데이터 정리
        items = []
        if 'response' in result and 'body' in result['response']:
            body = result['response']['body']
            
            # 'items' 항목이 있는 경우 처리
            if 'items' in body:
                item_container = body['items']
                
                # 'item'이 딕셔너리인 경우 (단일 항목)
                if 'item' in item_container:
                    item_data = item_container['item']
                    
                    # 단일 항목을 리스트로 변환하여 일관성 유지
                    if isinstance(item_data, dict):
                        items = [item_data]
                    # 이미 리스트인 경우
                    elif isinstance(item_data, list):
                        items = item_data
            
            # 결과가 비어있는 경우 빈 리스트 반환
            if not items:
                return {'items': []}
        
        return {'items': items}
    
    except Exception as e:
        print(f"XML 파싱 오류: {e}")
        return {'error': True, 'message': str(e)}