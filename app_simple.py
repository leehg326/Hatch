#!/usr/bin/env python3
"""
가벼운 Flask 앱 - 로그인 + 세션만
"""

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Flask 앱 생성
app = Flask(__name__)

# 기본 설정
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 설정 - 모든 경로에 대해 localhost:5173 허용
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
     expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
     vary_header=True,
     send_wildcard=False,
     always_send=True
)

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
    is_email_verified = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email or self.name}>'

# 라우트
@app.route('/auth/email/login', methods=['GET', 'POST', 'OPTIONS'])
def email_login():
    if request.method == 'GET':
        response = jsonify({'message': 'Login endpoint - use POST method'})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        data = request.get_json()
        print(f"Received login data: {data}")  # 디버깅용
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"Login attempt for email: {email}")  # 디버깅용
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        print(f"User found: {user}")  # 디버깅용
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.password_hash:
            return jsonify({'error': 'User has no password set'}), 401
        
        # Verify password (간단한 체크)
        if user.password_hash != password:
            print(f"Password mismatch. Expected: {user.password_hash}, Got: {password}")  # 디버깅용
            return jsonify({'error': 'Invalid password'}), 401
        
        # Set session
        session['user_id'] = user.id
        session['name'] = user.name
        print(f"Session set for user: {user.name}")  # 디버깅용
        
        response = jsonify({'ok': True})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # 상세한 오류 정보
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/auth/me', methods=['GET', 'OPTIONS'])
def get_session_user():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    uid = session.get('user_id')
    if not uid:
        response = jsonify(None)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Origin'
        return response, 401
    
    user = User.query.get(uid)
    if not user:
        response = jsonify(None)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Origin'
        return response, 401
    
    response = jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Origin'
    return response

@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    return jsonify({
        'contracts': [],
        'total': 0,
        'pages': 1,
        'current_page': 1,
        'per_page': 20
    })

@app.route('/auth')
def auth_info():
    return jsonify({'message': 'Auth endpoint - use /auth/email/login for login'})

@app.route('/health')
def health_check():
    try:
        # 데이터베이스 연결 테스트
        user_count = User.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'user_count': user_count
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 테스트 사용자 생성
        existing_user = User.query.filter_by(email='test@test.com').first()
        if not existing_user:
            user = User(
                name='테스트 사용자',
                email='test@test.com',
                password_hash='password123',  # 간단한 평문 저장
                is_email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            print('✅ 테스트 사용자 생성 완료!')
        else:
            print('✅ 테스트 사용자 이미 존재!')
    
    print('✅ 가벼운 Flask 앱 시작!')
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True, port=5000)
