from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ProviderType(Enum):
    KAKAO = 'kakao'
    GOOGLE = 'google'
    APPLE = 'apple'
    FACEBOOK = 'facebook'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)  # nullable for social-only users
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=True)  # nullable for social-only users
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    identities = db.relationship('Identity', backref='user', lazy=True, cascade='all, delete-orphan')
    password_resets = db.relationship('PasswordReset', backref='user', lazy=True, cascade='all, delete-orphan')
    email_verifications = db.relationship('EmailVerification', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email or self.name}>'

class Identity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider = db.Column(db.Enum(ProviderType), nullable=False)
    subject = db.Column(db.String(120), nullable=False)  # OAuth provider's user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint on provider + subject
    __table_args__ = (db.UniqueConstraint('provider', 'subject', name='_provider_subject_uc'),)

    def __repr__(self):
        return f'<Identity {self.provider.value}:{self.subject}>'

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PasswordReset {self.user_id}>'

class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False)  # SHA256 hash
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EmailVerification {self.user_id}>'

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    property_address = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # 원 단위
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    memo = db.Column(db.Text, nullable=True)
    signature_data = db.Column(db.Text, nullable=True)  # base64 encoded signature
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('contracts', lazy=True))

    def __repr__(self):
        return f'<Contract {self.customer_name} - {self.property_address}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'property_address': self.property_address,
            'price': self.price,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'memo': self.memo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
