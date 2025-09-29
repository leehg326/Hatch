import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, using environment variables only")

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET') or 'dev-secret-key'
    JWT_SECRET = os.environ.get('JWT_SECRET') or 'dev-jwt-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLIENT_ORIGIN = os.environ.get('CLIENT_ORIGIN') or 'http://localhost:5173'
    
    # OAuth Configuration
    KAKAO_CLIENT_ID = os.environ.get('KAKAO_CLIENT_ID')
    KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI')
    
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    
    FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
    FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
    FACEBOOK_REDIRECT_URI = os.environ.get('FACEBOOK_REDIRECT_URI')
    
    APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID')
    APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID')
    APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID')
    APPLE_PRIVATE_KEY_PATH = os.environ.get('APPLE_PRIVATE_KEY_PATH')
    APPLE_REDIRECT_URI = os.environ.get('APPLE_REDIRECT_URI')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER') or 'Hatch <no-reply@hatch.app>'
    
    # Security Settings
    JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7 days in seconds
    EMAIL_VERIFICATION_EXPIRES = 30 * 60  # 30 minutes
    PASSWORD_RESET_EXPIRES = 15 * 60  # 15 minutes
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Electronic Signature Configuration
    APP_BASE_URL = os.environ.get('APP_BASE_URL') or 'http://127.0.0.1:5000'
    SIGN_TOKEN_TTL_DAYS = int(os.environ.get('SIGN_TOKEN_TTL_DAYS') or 7)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'