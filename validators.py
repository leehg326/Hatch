# -*- coding: utf-8 -*-
"""
계약서 데이터 유효성 검증 모듈
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional


def to_int_safe(value: Any, field_name: str = "") -> tuple[int, str]:
    """
    안전한 정수 변환 (문자열·콤마 허용)
    
    Args:
        value: 변환할 값
        field_name: 필드명 (오류 메시지용)
        
    Returns:
        tuple[int, str]: (변환된 정수, 오류 메시지)
    """
    if value is None or value == "":
        return 0, f"{field_name}는 필수 항목입니다"
    
    try:
        if isinstance(value, int):
            return value, ""
        elif isinstance(value, str):
            # 콤마 제거 후 정수 변환
            cleaned = value.replace(',', '').strip()
            if not cleaned:
                return 0, f"{field_name}는 필수 항목입니다"
            return int(cleaned), ""
        elif isinstance(value, float):
            return int(value), ""
        else:
            return 0, f"{field_name}는 올바른 숫자 형식이 아닙니다"
    except (ValueError, TypeError):
        return 0, f"{field_name}는 올바른 숫자 형식이 아닙니다"


def validate_contract_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    계약서 페이로드 유효성 검증 (명시적·관대한 방식)
    
    Args:
        payload: 검증할 계약서 데이터
        
    Returns:
        Dict[str, str]: 오류가 있으면 {필드명: 오류메시지}, 없으면 빈 딕셔너리
    """
    errors = {}
    
    # 1. 모든 계약 유형 공통 필수 필드 검증 (공백만 입력도 오류 처리)
    common_required_fields = [
        'type', 'seller_name', 'seller_phone', 
        'buyer_name', 'buyer_phone', 'property_address'
    ]
    
    for field in common_required_fields:
        value = payload.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            errors[field] = f'{field}는 필수 항목입니다'
    
    # 2. 계약 유형 검증
    contract_type = payload.get('type')
    if contract_type and contract_type not in ['SALE', 'JEONSE', 'WOLSE', 'BANJEONSE']:
        errors['type'] = '유효하지 않은 계약 유형입니다'
    
    # 3. 전화번호 형식 검증 (간단한 검증)
    phone_fields = ['seller_phone', 'buyer_phone']
    for field in phone_fields:
        value = payload.get(field)
        if value and isinstance(value, str):
            # 숫자, 하이픈, 공백만 허용
            if not re.match(r'^[\d\-\s]+$', value.strip()):
                errors[field] = '올바른 전화번호 형식이 아닙니다'
    
    # 4. 계약 유형별 필수 필드 검증
    if contract_type == 'SALE':
        # 매매: sale_price 필수, deposit/monthly_rent는 null이어야 함
        sale_price, price_error = to_int_safe(payload.get('sale_price'), '매매가격')
        if price_error:
            errors['sale_price'] = price_error
        elif sale_price <= 0:
            errors['sale_price'] = '매매가격은 0보다 커야 합니다'
        
        # 매매에서는 deposit, monthly_rent가 있으면 안됨
        if payload.get('deposit') is not None:
            errors['deposit'] = '매매 계약에서는 보증금을 입력할 수 없습니다'
        if payload.get('monthly_rent') is not None:
            errors['monthly_rent'] = '매매 계약에서는 월세를 입력할 수 없습니다'
    
    elif contract_type == 'JEONSE':
        # 전세: deposit 필수, sale_price/monthly_rent는 null이어야 함
        deposit, deposit_error = to_int_safe(payload.get('deposit'), '전세보증금')
        if deposit_error:
            errors['deposit'] = deposit_error
        elif deposit <= 0:
            errors['deposit'] = '전세보증금은 0보다 커야 합니다'
        
        # 전세에서는 sale_price, monthly_rent가 있으면 안됨
        if payload.get('sale_price') is not None:
            errors['sale_price'] = '전세 계약에서는 매매가격을 입력할 수 없습니다'
        if payload.get('monthly_rent') is not None:
            errors['monthly_rent'] = '전세 계약에서는 월세를 입력할 수 없습니다'
    
    elif contract_type == 'WOLSE':
        # 월세: deposit + monthly_rent 필수, sale_price는 null이어야 함
        deposit, deposit_error = to_int_safe(payload.get('deposit'), '보증금')
        if deposit_error:
            errors['deposit'] = deposit_error
        elif deposit <= 0:
            errors['deposit'] = '보증금은 0보다 커야 합니다'
        
        monthly_rent, rent_error = to_int_safe(payload.get('monthly_rent'), '월세')
        if rent_error:
            errors['monthly_rent'] = rent_error
        elif monthly_rent <= 0:
            errors['monthly_rent'] = '월세는 0보다 커야 합니다'
        
        # 월세에서는 sale_price가 있으면 안됨
        if payload.get('sale_price') is not None:
            errors['sale_price'] = '월세 계약에서는 매매가격을 입력할 수 없습니다'
        
    
    return errors




def _validate_period(period: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """
    계약 기간 검증
    
    Args:
        period: 계약 기간 데이터 {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
        
    Returns:
        Dict[str, str]: 오류가 있으면 {필드명: 오류메시지}
    """
    errors = {}
    
    if not period:
        errors['period'] = '계약 기간은 필수 항목입니다'
        return errors
    
    start_date = period.get('start')
    end_date = period.get('end')
    
    if not start_date:
        errors['period.start'] = '계약 시작일은 필수 항목입니다'
    else:
        if not _is_valid_date_format(start_date):
            errors['period.start'] = '올바른 날짜 형식이 아닙니다 (YYYY-MM-DD)'
    
    if not end_date:
        errors['period.end'] = '계약 종료일은 필수 항목입니다'
    else:
        if not _is_valid_date_format(end_date):
            errors['period.end'] = '올바른 날짜 형식이 아닙니다 (YYYY-MM-DD)'
    
    # 시작일과 종료일이 모두 유효한 경우 날짜 순서 검증
    if start_date and end_date and not errors.get('period.start') and not errors.get('period.end'):
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt >= end_dt:
                errors['period'] = '계약 시작일은 종료일보다 이전이어야 합니다'
        except ValueError:
            # 이미 위에서 형식 오류를 처리했으므로 여기서는 무시
            pass
    
    return errors


def _is_valid_date_format(date_str: str) -> bool:
    """
    날짜 형식 검증 (YYYY-MM-DD)
    
    Args:
        date_str: 검증할 날짜 문자열
        
    Returns:
        bool: 유효한 형식이면 True
    """
    if not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
