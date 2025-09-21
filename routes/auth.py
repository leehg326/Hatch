"""
Authentication routes for email/password login
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
from models import db, User
from auth_utils import create_access_token, create_refresh_token, decode_token, auth_required

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# JWT 설정은 auth_utils.py에서 가져옴

@bp.route('/signup', methods=['POST'])
def signup():
    """회원가입"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # 유효성 검사
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # 중복 이메일 확인
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 409
        
        # 사용자 생성
        user = User(
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
            name=name if name else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """로그인"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # 사용자 찾기
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # 토큰 생성
        access_token = create_access_token(user.id, user.email, user.name)
        refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/refresh', methods=['POST'])
def refresh():
    """토큰 갱신"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        refresh_token = data.get('refresh_token', '')
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        # 리프레시 토큰 검증
        try:
            payload = decode_token(refresh_token, 'refresh')
            user_id = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        # 사용자 확인
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # 새 토큰 생성
        access_token = create_access_token(user.id, user.email, user.name)
        new_refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500

@bp.route('/me', methods=['GET'])
@auth_required
def get_current_user(user):
    """현재 사용자 정보"""
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'created_at': user.created_at.isoformat()
    })

@bp.route('/logout', methods=['POST'])
def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return jsonify({'message': 'Logged out successfully'})
