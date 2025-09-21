from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import os
from config import Config
from models import db, User, Identity, PasswordReset, EmailVerification, ProviderType
from security import (
    hash_password, verify_password, generate_token, hash_token, verify_token_hash,
    generate_jwt_token, verify_jwt_token, generate_email_verification_token,
    verify_email_verification_token, generate_password_reset_token, verify_password_reset_token
)
from mailer import mailer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"]
    )
    
    # Initialize OAuth
    oauth = OAuth(app)
    
    # Configure OAuth providers
    if Config.GOOGLE_CLIENT_ID:
        oauth.register(
            name='google',
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
    
    if Config.FACEBOOK_CLIENT_ID:
        oauth.register(
            name='facebook',
            client_id=Config.FACEBOOK_CLIENT_ID,
            client_secret=Config.FACEBOOK_CLIENT_SECRET,
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
            expires_at = datetime.utcnow() + timedelta(seconds=Config.EMAIL_VERIFICATION_EXPIRES)
            
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
    
    @app.route('/auth/email/login', methods=['POST'])
    @limiter.limit("5 per minute")
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
            
            # Verify password
            if not verify_password(password, user.password_hash):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check email verification
            if not user.is_email_verified:
                return jsonify({'error': 'Email not verified', 'reason': 'email_not_verified'}), 401
            
            # Generate JWT token
            token = generate_jwt_token(user.id, user.email, user.name)
            
            return jsonify({'token': token})
            
        except Exception as e:
            return jsonify({'error': 'Login failed'}), 500
    
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
                expires_at = datetime.utcnow() + timedelta(seconds=Config.PASSWORD_RESET_EXPIRES)
                
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
        if provider not in ['google', 'facebook']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        if provider == 'google' and not Config.GOOGLE_CLIENT_ID:
            return jsonify({'error': 'Google OAuth not configured'}), 400
        if provider == 'facebook' and not Config.FACEBOOK_CLIENT_ID:
            return jsonify({'error': 'Facebook OAuth not configured'}), 400
        
        redirect_uri = url_for('oauth_callback', provider=provider, _external=True)
        return oauth.__getattr__(provider).authorize_redirect(redirect_uri)
    
    @app.route('/auth/<provider>/callback')
    @limiter.limit("20 per minute")
    def oauth_callback(provider):
        if provider not in ['google', 'facebook']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        try:
            oauth_client = oauth.__getattr__(provider)
            token = oauth_client.authorize_access_token()
            
            # Get user info
            if provider == 'google':
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
                return jsonify({'error': 'Failed to get user info'}), 400
            
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
            return redirect(f"{Config.CLIENT_ORIGIN}/oauth-complete?token={jwt_token}")
            
        except Exception as e:
            return jsonify({'error': 'OAuth authentication failed'}), 500
    
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
    
    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)






