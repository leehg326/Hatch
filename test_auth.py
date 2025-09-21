#!/usr/bin/env python3
"""
인증 API 테스트 스크립트
"""
import requests
import json

def test_auth_api():
    base_url = "http://localhost:5000"
    
    # 1. 회원가입 테스트
    print("=== 회원가입 테스트 ===")
    signup_data = {
        "email": "test@example.com",
        "password": "test123456",
        "name": "테스트사용자"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"회원가입 오류: {e}")
    
    print("\n=== 로그인 테스트 ===")
    # 2. 로그인 테스트
    login_data = {
        "email": "test@example.com",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            access_token = result.get('access_token')
            print(f"Access Token: {access_token[:50]}...")
            
            # 3. 사용자 정보 조회 테스트
            print("\n=== 사용자 정보 조회 테스트 ===")
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
            print(f"Status: {me_response.status_code}")
            print(f"User Info: {me_response.json()}")
            
    except Exception as e:
        print(f"로그인 오류: {e}")

if __name__ == "__main__":
    test_auth_api()
