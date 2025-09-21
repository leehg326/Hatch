from flask import Flask, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import os
import config
from models import db, User, Identity, PasswordReset, EmailVerification, ProviderType, Contract
from security import (
    hash_password, verify_password, generate_token, hash_token, verify_token_hash,
    generate_jwt_token, verify_jwt_token, generate_email_verification_token,
    verify_email_verification_token, generate_password_reset_token, verify_password_reset_token
)
from mailer import mailer
from pdf_generator import ContractPDFGenerator
from flask import make_response
from routes.auth import bp as auth_bp

def create_app():
    app = Flask(__name__)
    
    # Config 클래스에서 설정 로드
    try:
        app.config.from_object(config.Config)
    except Exception as e:
        print(f"Config 로드 실패: {e}")
    
    # 설정 강제 적용
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['CLIENT_ORIGIN'] = 'http://localhost:5173'
    
    # CORS 설정 - 모든 경로에 대해 localhost:5173 허용
    ALLOWED_ORIGINS = {"http://localhost:5173", "http://127.0.0.1:5173"}
    CORS(app, 
         resources={r"/*": {"origins": list(ALLOWED_ORIGINS)}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
         expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
         vary_header=True,
         send_wildcard=False,
         always_send=True
    )
    
    # 모든 응답에 CORS 보장
    @app.after_request
    def add_cors_headers(resp):
        origin = request.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        return resp
    
    # 세션 설정
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # 개발 환경
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None  # 모든 도메인에서 접근 가능
    app.config['SESSION_COOKIE_PATH'] = '/'  # 모든 경로에서 접근 가능
    
    # 설정 확인
    print(f"DB 설정 확인: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["1000 per hour"]  # 개발 환경용으로 제한 완화
    )
    
    # Initialize OAuth
    oauth = OAuth(app)
    
    # Configure OAuth providers
    if config.Config.KAKAO_CLIENT_ID:
        # 카카오 OIDC/OAuth2 토글 설정
        USE_OIDC = os.getenv("KAKAO_USE_OIDC", "true").lower() == "true"
        KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
        
        if USE_OIDC:
            # OIDC 모드
            oauth.register(
                name='kakao',
                client_id=config.Config.KAKAO_CLIENT_ID,
                client_secret=KAKAO_CLIENT_SECRET,
                server_metadata_url='https://kauth.kakao.com/.well-known/openid-configuration',
                api_base_url='https://kapi.kakao.com/',
                client_kwargs={'scope': 'openid profile account_email'},
            )
        else:
            # OAuth2 모드
            oauth.register(
                name='kakao',
                client_id=config.Config.KAKAO_CLIENT_ID,
                client_secret=KAKAO_CLIENT_SECRET,
                authorize_url='https://kauth.kakao.com/oauth/authorize',
                access_token_url='https://kauth.kakao.com/oauth/token',
                api_base_url='https://kapi.kakao.com/',
                client_kwargs={'scope': 'profile account_email'},
            )
    
    if config.Config.GOOGLE_CLIENT_ID:
        oauth.register(
            name='google',
            client_id=config.Config.GOOGLE_CLIENT_ID,
            client_secret=config.Config.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
    
    if config.Config.FACEBOOK_CLIENT_ID:
        oauth.register(
            name='facebook',
            client_id=config.Config.FACEBOOK_CLIENT_ID,
            client_secret=config.Config.FACEBOOK_CLIENT_SECRET,
            access_token_url='https://graph.facebook.com/oauth/access_token',
            authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
            api_base_url='https://graph.facebook.com/',
            client_kwargs={'scope': 'email'}
        )
    
    # Helper functions
    def get_current_user():
        """Get current user from JWT token"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            payload = verify_jwt_token(token)
            return User.query.get(payload['sub'])
        except:
            return None
    
    def require_auth(f):
        """Decorator to require authentication"""
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            return f(user, *args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    # Email/Password Authentication Routes
    @app.route('/auth/email/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def email_register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            # Validation
            if not name or len(name) < 2:
                return jsonify({'error': 'Name must be at least 2 characters'}), 400
            if not email or '@' not in email:
                return jsonify({'error': 'Valid email is required'}), 400
            if not password or len(password) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create user
            user = User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                is_email_verified=False
            )
            db.session.add(user)
            db.session.commit()
            
            # Generate email verification token
            token = generate_token()
            token_hash = hash_token(token)
            expires_at = datetime.utcnow() + timedelta(seconds=config.Config.EMAIL_VERIFICATION_EXPIRES)
            
            email_verification = EmailVerification(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at
            )
            db.session.add(email_verification)
            db.session.commit()
            
            # Send verification email
            mailer.send_email_verification(email, name, token)
            
            return jsonify({'message': 'Registration successful. Please check your email for verification.'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/auth/email/login', methods=['POST', 'OPTIONS'])
    @limiter.limit("5 per minute")
    def email_login():
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
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
            
            # Verify password
            if not verify_password(password, user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check email verification (disabled for new auth system)
            # if not user.is_email_verified:
            #     return jsonify({'error': 'Email not verified', 'reason': 'email_not_verified'}), 401
            
            # Set session
            session['user_id'] = user.id
            session['name'] = user.name
            
            print(f"Session set for user {user.id}: {dict(session)}")
            
            return jsonify({
                'ok': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            })
            
        except Exception as e:
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/auth/logout', methods=['POST', 'OPTIONS'])
    def logout():
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            # Clear session
            session.clear()
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'error': 'Logout failed'}), 500
    
    @app.route('/auth/email/verify', methods=['POST'])
    @limiter.limit("5 per minute")
    def email_verify():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            token = data.get('token', '').strip()
            if not token:
                return jsonify({'error': 'Token is required'}), 400
            
            # Find verification record
            token_hash = hash_token(token)
            verification = EmailVerification.query.filter_by(
                token_hash=token_hash,
                used=False
            ).first()
            
            if not verification:
                return jsonify({'error': 'Invalid or expired token'}), 400
            
            if verification.expires_at < datetime.utcnow():
                return jsonify({'error': 'Token has expired'}), 400
            
            # Update user and verification
            verification.user.is_email_verified = True
            verification.used = True
            db.session.commit()
            
            return jsonify({'message': 'Email verified successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Verification failed'}), 500
    
    @app.route('/auth/email/forgot', methods=['POST'])
    @limiter.limit("5 per minute")
    def email_forgot():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            
            # Find user (always return success for security)
            user = User.query.filter_by(email=email).first()
            if user and user.password_hash:
                # Generate password reset token
                token = generate_token()
                token_hash = hash_token(token)
                expires_at = datetime.utcnow() + timedelta(seconds=config.Config.PASSWORD_RESET_EXPIRES)
                
                password_reset = PasswordReset(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at
                )
                db.session.add(password_reset)
                db.session.commit()
                
                # Send reset email
                mailer.send_password_reset(email, user.name, token)
            
            return jsonify({'message': 'If the email exists, a reset link has been sent'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Request failed'}), 500
    
    @app.route('/auth/email/reset', methods=['POST'])
    @limiter.limit("5 per minute")
    def email_reset():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            token = data.get('token', '').strip()
            new_password = data.get('new_password', '')
            
            if not token or not new_password:
                return jsonify({'error': 'Token and new password are required'}), 400
            
            if len(new_password) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            
            # Find reset record
            token_hash = hash_token(token)
            reset_record = PasswordReset.query.filter_by(
                token_hash=token_hash,
                used=False
            ).first()
            
            if not reset_record:
                return jsonify({'error': 'Invalid or expired token'}), 400
            
            if reset_record.expires_at < datetime.utcnow():
                return jsonify({'error': 'Token has expired'}), 400
            
            # Update password
            reset_record.user.password_hash = hash_password(new_password)
            reset_record.used = True
            db.session.commit()
            
            return jsonify({'message': 'Password reset successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Reset failed'}), 500
    
    # Social OAuth Routes
    @app.route('/auth/<provider>')
    @limiter.limit("20 per minute")
    def oauth_authorize(provider):
        if provider not in ['kakao', 'google', 'facebook']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        # Provider별 설정 확인
        if provider == 'kakao' and not config.Config.KAKAO_CLIENT_ID:
            return jsonify({'error': 'Kakao OAuth not configured'}), 400
        if provider == 'google' and not config.Config.GOOGLE_CLIENT_ID:
            return jsonify({'error': 'Google OAuth not configured'}), 400
        if provider == 'facebook' and not config.Config.FACEBOOK_CLIENT_ID:
            return jsonify({'error': 'Facebook OAuth not configured'}), 400
        
        redirect_uri = url_for('oauth_callback', provider=provider, _external=True)
        try:
            return oauth.__getattr__(provider).authorize_redirect(redirect_uri)
        except Exception as e:
            app.logger.exception(f"OAuth authorize_redirect failed for {provider}: {e}")
            return jsonify({"error": "kakao_discovery_failed"}), 502
    
    @app.route('/auth/<provider>/callback')
    @limiter.limit("20 per minute")
    def oauth_callback(provider):
        if provider not in ['kakao', 'google', 'facebook']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        try:
            oauth_client = oauth.__getattr__(provider)
            token = oauth_client.authorize_access_token()
            
            # Get user info based on provider
            if provider == 'kakao':
                # 카카오 OIDC/OAuth2 분기 처리
                USE_OIDC = os.getenv("KAKAO_USE_OIDC", "true").lower() == "true"
                
                if USE_OIDC:
                    # OIDC 모드: userinfo 엔드포인트 사용
                    try:
                        resp = oauth_client.get('v1/oidc/userinfo', token=token)
                        user_info = resp.json()
                        subject = str(user_info.get('sub', user_info.get('id')))
                        email = user_info.get('email')
                        name = user_info.get('name', user_info.get('nickname'))
                    except Exception as e:
                        app.logger.warning(f"OIDC userinfo failed, falling back to v2/user/me: {e}")
                        # OIDC 실패 시 OAuth2 방식으로 폴백
                        resp = oauth_client.get('v2/user/me', token=token)
                        user_info = resp.json()
                        subject = str(user_info.get('id'))
                        email = user_info.get('kakao_account', {}).get('email')
                        name = user_info.get('kakao_account', {}).get('profile', {}).get('nickname')
                else:
                    # OAuth2 모드: v2/user/me 사용
                    resp = oauth_client.get('v2/user/me', token=token)
                    user_info = resp.json()
                    subject = str(user_info.get('id'))
                    email = user_info.get('kakao_account', {}).get('email')
                    name = user_info.get('kakao_account', {}).get('profile', {}).get('nickname')
                
                # 이메일/닉네임 파싱 실패 시 400 반환
                if not email and not name:
                    app.logger.error(f"Failed to parse Kakao user info: {user_info}")
                    return jsonify({'error': 'Failed to get user profile from Kakao'}), 400
                
            elif provider == 'google':
                user_info = token.get('userinfo')
                if not user_info:
                    return jsonify({'error': 'Failed to get user info'}), 400
                
                subject = user_info.get('sub')
                email = user_info.get('email')
                name = user_info.get('name')
                
            elif provider == 'facebook':
                resp = oauth_client.get('me?fields=id,name,email')
                user_info = resp.json()
                subject = user_info.get('id')
                email = user_info.get('email')
                name = user_info.get('name')
            
            if not subject or not name:
                print(f"OAuth error for {provider}: Missing subject or name")
                return redirect(f"{config.Config.CLIENT_ORIGIN}/oauth-complete?error=login_failed")
            
            # Find or create user
            identity = Identity.query.filter_by(
                provider=ProviderType(provider),
                subject=subject
            ).first()
            
            if identity:
                user = identity.user
            else:
                # Create new user
                user = User(
                    name=name,
                    email=email,
                    is_email_verified=True if email else False
                )
                db.session.add(user)
                db.session.flush()  # Get user ID
                
                # Create identity
                identity = Identity(
                    user_id=user.id,
                    provider=ProviderType(provider),
                    subject=subject
                )
                db.session.add(identity)
                db.session.commit()
            
            # Generate JWT token
            jwt_token = generate_jwt_token(user.id, user.email or '', user.name)
            
            # Redirect to frontend with token
            return redirect(f"{config.Config.CLIENT_ORIGIN}/oauth-complete?token={jwt_token}")
            
        except Exception as e:
            print(f"OAuth callback error for {provider}: {str(e)}")
            return redirect(f"{config.Config.CLIENT_ORIGIN}/oauth-complete?error=login_failed")
    
    # Protected routes
    @app.route('/me')
    @require_auth
    def get_current_user_info(user):
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'is_email_verified': user.is_email_verified,
            'created_at': user.created_at.isoformat()
        })
    
    # Session-based auth endpoint
    @app.route('/auth/me', methods=['GET', 'OPTIONS'])
    def get_session_user():
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        print(f"Session data: {dict(session)}")
        print(f"Request cookies: {dict(request.cookies)}")
        
        uid = session.get('user_id')
        if not uid:
            print("No user_id in session")
            return jsonify(None), 401
        user = User.query.get(uid)
        if not user:
            print(f"User {uid} not found in database")
            return jsonify(None), 401
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email
        })
    
    # Contract API Routes
    @app.route('/api/contracts', methods=['POST'])
    @require_auth
    def create_contract(user):
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # 필수 필드 검증
            required_fields = ['customer_name', 'customer_phone', 'property_address', 'price', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # 날짜 형식 검증
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            # 계약서 생성
            contract = Contract(
                user_id=user.id,
                customer_name=data['customer_name'].strip(),
                customer_phone=data['customer_phone'].strip(),
                property_address=data['property_address'].strip(),
                price=int(data['price']),
                start_date=start_date,
                end_date=end_date,
                memo=data.get('memo', '').strip(),
                signature_data=data.get('signature_data', '')
            )
            
            db.session.add(contract)
            db.session.commit()
            
            return jsonify({
                'message': 'Contract created successfully',
                'contract': contract.to_dict()
            }), 201
            
        except ValueError as e:
            return jsonify({'error': 'Invalid data format'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create contract'}), 500
    
    @app.route('/api/contracts', methods=['GET'])
    # @require_auth  # 임시로 비활성화
    def get_contracts(user=None):
        try:
            # 검색 쿼리 파라미터
            search_query = request.args.get('q', '').strip()
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # 기본 쿼리 (사용자의 계약서만)
            if user:
                query = Contract.query.filter_by(user_id=user.id)
            else:
                # 인증되지 않은 경우 모든 계약서 조회 (개발용)
                query = Contract.query
            
            # 검색 필터 적용
            if search_query:
                search_filter = f"%{search_query}%"
                query = query.filter(
                    db.or_(
                        Contract.customer_name.ilike(search_filter),
                        Contract.customer_phone.ilike(search_filter),
                        Contract.property_address.ilike(search_filter)
                    )
                )
            
            # 최신순 정렬 및 페이지네이션
            contracts = query.order_by(Contract.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'contracts': [contract.to_dict() for contract in contracts.items],
                'total': contracts.total,
                'pages': contracts.pages,
                'current_page': page,
                'per_page': per_page
            })
            
        except Exception as e:
            return jsonify({'error': 'Failed to fetch contracts'}), 500
    
    @app.route('/api/contracts/<int:contract_id>', methods=['GET'])
    @require_auth
    def get_contract(user, contract_id):
        try:
            contract = Contract.query.filter_by(id=contract_id, user_id=user.id).first()
            if not contract:
                return jsonify({'error': 'Contract not found'}), 404
            
            return jsonify({'contract': contract.to_dict()})
            
        except Exception as e:
            return jsonify({'error': 'Failed to fetch contract'}), 500
    
    @app.route('/api/contracts/<int:contract_id>/pdf', methods=['GET'])
    @require_auth
    def get_contract_pdf(user, contract_id):
        try:
            contract = Contract.query.filter_by(id=contract_id, user_id=user.id).first()
            if not contract:
                return jsonify({'error': 'Contract not found'}), 404
            
            # PDF 생성
            pdf_generator = ContractPDFGenerator()
            pdf_data = pdf_generator.generate_contract_pdf(contract)
            
            # PDF 응답 생성
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="contract_{contract_id}.pdf"'
            
            return response
            
        except Exception as e:
            return jsonify({'error': 'Failed to generate PDF'}), 500
    
    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # 라우트 목록 디버그 (개발 전용)
    @app.route('/__routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "rule": str(rule),
                "endpoint": rule.endpoint,
                "methods": sorted(list(rule.methods - {"HEAD", "OPTIONS"})),
            })
        return jsonify(routes=routes)
    
    
    
    # /contracts Shim 라우트 (404 방지)
    @app.route('/contracts', methods=['GET'])
    @limiter.limit("1000 per hour")  # 대시보드용으로 제한 완화
    def contracts_shim():
        """
        대시보드가 기대하는 /contracts 엔드포인트에 대한 임시 호환 라우트.
        - 실제 구현(/api/contracts, /contracts/list 등)이 따로 있으면,
          그쪽을 호출하게 리팩터 가능. 우선은 최소 형태로 200 보장.
        """
        per_page = request.args.get("per_page", default=5, type=int)
        page = request.args.get("page", default=1, type=int)

        # TODO: 실제 구현이 있을 경우 여기서 위임/연결:
        #   from .contracts_bp import list_contracts
        #   return list_contracts()

        # 임시 최소 응답(프런트가 크래시하지 않게 표준형 제공)
        return jsonify({
            "items": [],          # 실제 데이터 없으면 빈 배열
            "total": 0,           # 전체 개수
            "page": page,
            "per_page": per_page
        }), 200
    
    # Register auth blueprint
    app.register_blueprint(auth_bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception(error)
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
