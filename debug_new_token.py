#!/usr/bin/env python3
"""
새로운 토큰 디버깅
"""
import jwt
import os

# JWT 설정
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')

def debug_new_token():
    # 새로운 테스트에서 받은 토큰
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjMsImVtYWlsIjoibmV3dXNlckBleGFtcGxlLmNvbSIsIm5hbWUiOiJcdWMwYzhcdWMwYWNcdWM2YTlcdWM3OTAiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3OTM3OTM5LCJpYXQiOjE3NTc5MzcwMzl9.HZzGVDW987POB172BmdWRxKQH8R5TlTiRuXQbq1Xy5Q"
    
    print(f"JWT_SECRET: {JWT_SECRET}")
    print(f"Token: {token}")
    
    try:
        # 토큰 디코딩 (검증 없이)
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"Decoded payload: {decoded}")
        
        # 토큰 검증
        verified = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(f"Verified payload: {verified}")
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    debug_new_token()
