#!/usr/bin/env python3
"""
간단한 Flask 앱 - DB 설정 문제 해결용
"""

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import check_password_hash
import os

# Flask 앱 생성
app = Flask(__name__)

# 설정 직접 적용
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 설정
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]},
    r"/auth/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}
}, supports_credentials=True)

# 세션 설정
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# SQLAlchemy 초기화
db = SQLAlchemy(app)

# 간단한 User 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=True)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email or self.name}>'

# 라우트
@app.route('/auth/email/login', methods=['POST'])
def email_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password (간단한 체크)
        if user.password_hash != password:  # 실제로는 해시 비교해야 함
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_id'] = user.id
        session['name'] = user.name
        
        return jsonify({'ok': True})
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/me')
def get_session_user():
    uid = session.get('user_id')
    if not uid:
        return jsonify(None), 401
    user = User.query.get(uid)
    if not user:
        return jsonify(None), 401
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    return jsonify({
        'contracts': [],
        'total': 0,
        'pages': 1,
        'current_page': 1,
        'per_page': 20
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 테스트 사용자 생성
        existing_user = User.query.filter_by(email='test@test.com').first()
        if not existing_user:
            user = User(
                name='테스트 사용자',
                email='test@test.com',
                password_hash='password123',  # 실제로는 해시해야 함
                is_email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            print('✅ 테스트 사용자 생성 완료!')
        else:
            print('✅ 테스트 사용자 이미 존재!')
    
    print('✅ Flask 앱 시작!')
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True, port=5000)
