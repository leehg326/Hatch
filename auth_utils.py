"""
Authentication utilities for JWT token management
"""
import jwt
from datetime import datetime, timedelta
import os
from functools import wraps
from flask import request, jsonify
from models import User

# JWT 설정
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
ACCESS_TOKEN_EXPIRES_MIN = int(os.environ.get('ACCESS_TOKEN_EXPIRES_MIN', '15'))
REFRESH_TOKEN_EXPIRES_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRES_DAYS', '14'))

def create_access_token(user_id, email, name):
    """액세스 토큰 생성"""
    payload = {
        'sub': user_id,
        'email': email,
        'name': name,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def create_refresh_token(user_id):
    """리프레시 토큰 생성"""
    payload = {
        'sub': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token, token_type='access'):
    """토큰 디코딩 및 검증"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # 토큰 타입 확인
        if payload.get('type') != token_type:
            raise jwt.InvalidTokenError('Invalid token type')
        
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token has expired')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token')

def auth_required(f):
    """인증이 필요한 엔드포인트 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = decode_token(token, 'access')
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({'error': 'Invalid token payload'}), 401
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return f(user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function
