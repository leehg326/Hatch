import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from config import Config

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token serializer for email verification and password reset
token_serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def generate_token() -> str:
    """Generate a random 32-byte token (base64url encoded)"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash a token using SHA256 for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its hash"""
    return hash_token(token) == token_hash

def generate_jwt_token(user_id: int, email: str, name: str) -> str:
    """Generate a JWT token for user authentication"""
    payload = {
        'sub': user_id,
        'email': email,
        'name': name,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def generate_email_verification_token(user_id: int) -> str:
    """Generate a secure token for email verification"""
    return token_serializer.dumps(
        {'user_id': user_id, 'type': 'email_verification'},
        salt='email-verification'
    )

def verify_email_verification_token(token: str, max_age: int = None) -> dict:
    """Verify email verification token"""
    if max_age is None:
        max_age = Config.EMAIL_VERIFICATION_EXPIRES
    try:
        return token_serializer.loads(
            token, 
            salt='email-verification', 
            max_age=max_age
        )
    except Exception:
        raise ValueError("Invalid or expired token")

def generate_password_reset_token(user_id: int) -> str:
    """Generate a secure token for password reset"""
    return token_serializer.dumps(
        {'user_id': user_id, 'type': 'password_reset'},
        salt='password-reset'
    )

def verify_password_reset_token(token: str, max_age: int = None) -> dict:
    """Verify password reset token"""
    if max_age is None:
        max_age = Config.PASSWORD_RESET_EXPIRES
    try:
        return token_serializer.loads(
            token, 
            salt='password-reset', 
            max_age=max_age
        )
    except Exception:
        raise ValueError("Invalid or expired token")






