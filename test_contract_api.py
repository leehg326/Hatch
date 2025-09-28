#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_contract_creation():
    """계약서 생성 API 테스트"""
    
    # 테스트 데이터
    test_data = {
        "type": "SALE",
        "seller_name": "홍길동",
        "seller_phone": "010-1234-5678",
        "buyer_name": "김철수", 
        "buyer_phone": "010-9876-5432",
        "property_address": "서울시 강남구 테헤란로 123",
        "price_total": 500000000,
        "period": {
            "start": "2025-01-01",
            "end": "2025-12-31"
        },
        "special_terms": "테스트 계약서입니다."
    }
    
    try:
        # API 호출
        response = requests.post(
            'http://127.0.0.1:5000/api/contracts',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 계약서 생성 성공! ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ 계약서 생성 실패: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def test_contract_list():
    """계약서 목록 조회 API 테스트"""
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/contracts')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 계약서 목록 조회 성공! 총 {result.get('total', 0)}개")
            return result
        else:
            print(f"❌ 계약서 목록 조회 실패: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def test_contract_pdf(contract_id):
    """계약서 PDF 생성 API 테스트"""
    
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/contracts/{contract_id}/pdf')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ PDF 생성 성공! 크기: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ PDF 생성 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("=== 계약서 API 테스트 시작 ===")
    
    # 1. 계약서 생성 테스트
    print("\n1. 계약서 생성 테스트")
    contract_id = test_contract_creation()
    
    # 2. 계약서 목록 조회 테스트
    print("\n2. 계약서 목록 조회 테스트")
    test_contract_list()
    
    # 3. PDF 생성 테스트 (계약서가 생성된 경우)
    if contract_id:
        print(f"\n3. PDF 생성 테스트 (ID: {contract_id})")
        test_contract_pdf(contract_id)
    
    print("\n=== 테스트 완료 ===")
