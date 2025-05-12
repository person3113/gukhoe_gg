import xmltodict
from typing import Dict, Any, Optional

def parse_xml_to_dict(xml_string: str) -> Dict[str, Any]:
    """
    XML 문자열을 파이썬 딕셔너리로 변환 (최소한의 처리만 수행)
    
    Args:
        xml_string: XML 형식의 문자열
    
    Returns:
        Dict[str, Any]: 변환된 딕셔너리
    """
    try:
        # XML 문자열을 딕셔너리로 변환
        result = xmltodict.parse(xml_string)
        
        # 기본 오류 체크
        if isinstance(result, dict) and 'OpenAPI_ServiceResponse' in result:
            service_result = result['OpenAPI_ServiceResponse'].get('cmmMsgHeader', {})
            if service_result.get('returnReasonCode') != '00':
                error_msg = service_result.get('errMsg', '알 수 없는 오류')
                print(f"API 응답 오류: {error_msg}")
                return {'error': True, 'message': error_msg}
        
        # 결과 반환 (원본 구조 유지)
        return result
        
    except Exception as e:
        print(f"XML 파싱 오류: {str(e)}")
        return {'error': True, 'message': str(e)}