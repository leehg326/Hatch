#!/usr/bin/env python3
"""
토큰 디버깅 스크립트
"""
import jwt
import os
from datetime import datetime

# JWT 설정
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')

def debug_token():
    # 테스트에서 받은 토큰
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsIm5hbWUiOiLthYzsiqTtirXsiqTtirUiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3OTM3NjE4LCJpYXQiOjE3NTc5MzY3MTh9.HIztgiw6lRQkcVNKFaCFFMT-GBGuWPNEi1SR_KZGqPE"
    
    print(f"JWT_SECRET: {JWT_SECRET}")
    print(f"Token: {token}")
    
    try:
        # 토큰 디코딩 (검증 없이)
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"Decoded payload: {decoded}")
        
        # 토큰 검증
        verified = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(f"Verified payload: {verified}")
        
        # 토큰 타입 확인
        token_type = verified.get('type')
        print(f"Token type: {token_type}")
        
        if token_type != 'access':
            print("ERROR: Token type mismatch!")
        else:
            print("Token type is correct")
            
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    debug_token()
