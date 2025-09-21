#!/usr/bin/env python3
"""
새로운 사용자로 인증 API 테스트
"""
import requests
import json

def test_new_user():
    base_url = "http://localhost:5000"
    
    # 새로운 사용자로 회원가입
    print("=== 새로운 사용자 회원가입 ===")
    signup_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "name": "새사용자"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("\n=== 로그인 테스트 ===")
            login_data = {
                "email": "newuser@example.com",
                "password": "password123"
            }
            
            response = requests.post(f"{base_url}/api/auth/login", json=login_data)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                access_token = result.get('access_token')
                print(f"Access Token: {access_token}")
                
                # 사용자 정보 조회
                print("\n=== 사용자 정보 조회 ===")
                headers = {"Authorization": f"Bearer {access_token}"}
                me_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
                print(f"Status: {me_response.status_code}")
                print(f"User Info: {me_response.json()}")
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    test_new_user()
