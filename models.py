from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Signature models will be imported after they are defined

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

# 기존 Contract 클래스는 새로운 Contract 클래스로 교체됨

# 새로운 Contract 모델들을 직접 정의
import json
import hashlib
import secrets
from datetime import date

class ContractType(Enum):
    SALE = 'SALE'           # 매매
    JEONSE = 'JEONSE'       # 전세
    WOLSE = 'WOLSE'         # 월세
    BANJEONSE = 'BANJEONSE' # 반전세

class ContractStatus(Enum):
    DRAFT = 'DRAFT'         # 초안
    SIGNED = 'SIGNED'       # 서명완료
    ARCHIVED = 'ARCHIVED'   # 보관

class SignatureRole(Enum):
    SELLER = 'SELLER'       # 매도인
    BUYER = 'BUYER'         # 매수인
    AGENT = 'AGENT'         # 중개사
    LESSOR = 'LESSOR'       # 임대인
    LESSEE = 'LESSEE'       # 임차인
    BROKER = 'BROKER'       # 중개인

class AuthMethod(Enum):
    MOBILE = 'MOBILE'       # 휴대폰 인증
    CERT = 'CERT'           # 공인인증서

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.Enum(ContractType), nullable=False)
    form_version = db.Column(db.String(50), default='협회_표준_2025-01-01')
    status = db.Column(db.Enum(ContractStatus), default=ContractStatus.DRAFT)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('contracts', lazy=True))
    sign_requests = db.relationship('SignRequest', backref='contract', lazy=True, cascade='all, delete-orphan')
    
    # 당사자 정보
    seller_name = db.Column(db.String(100), nullable=False)
    seller_phone = db.Column(db.String(20), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_phone = db.Column(db.String(20), nullable=False)
    
    # 개인정보 보호 (해시/암호화)
    seller_pid_hash = db.Column(db.String(64))  # 주민 앞6자리 또는 생년월일 해시
    buyer_pid_hash = db.Column(db.String(64))
    
    # 부동산 정보
    property_address = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.JSON)  # 동/호/면적 등
    
    # 계약 금액 (타입별 분리)
    sale_price = db.Column(db.Integer, nullable=True)  # 매매가격
    deposit = db.Column(db.Integer, nullable=True)      # 보증금
    monthly_rent = db.Column(db.Integer, nullable=True) # 월차임
    monthly_payday = db.Column(db.Integer)  # 매월 지급일 (1-31)
    
    # 호환성을 위한 기존 필드 (deprecated)
    price_total = db.Column(db.Integer)  # 매매 총액 (deprecated)
    
    # 관리비
    mgmt_fee = db.Column(db.Integer)     # 관리비 금액
    mgmt_note = db.Column(db.Text)       # 관리비 포함 항목
    
    # 계약 날짜 (직접 필드)
    contract_date = db.Column(db.Date, nullable=True)  # 계약일
    handover_date = db.Column(db.Date, nullable=True)  # 인도일
    
    # 일정 (JSON) - 기존 호환성 유지
    schedule = db.Column(db.JSON)  # contract/middle/balance/transfer/handover
    
    # 중개사 정보 (JSON)
    brokerage = db.Column(db.JSON)  # office_name/rep/reg_no/address/phone/fee/fee_note
    
    # 첨부파일 메타데이터 (JSON)
    attachments = db.Column(db.JSON)  # 등기부/건축물/토지 파일 메타
    
    # 특약사항
    special_terms = db.Column(db.Text)
    
    # 문서 정보
    doc_no = db.Column(db.String(24), unique=True)  # 문서번호
    doc_hash = db.Column(db.String(64))             # 원문 해시
    # pdf_sha256 = db.Column(db.String(64))           # PDF 해시 (임시 비활성화)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.doc_no:
            self.doc_no = self.generate_doc_no()
    
    def generate_doc_no(self):
        """문서번호 생성: CONTRACT_YYYYMMDD_XXXXXX"""
        today = datetime.now().strftime('%Y%m%d')
        random_suffix = secrets.token_hex(3).upper()
        return f"CONTRACT_{today}_{random_suffix}"
    
    def calculate_hash(self):
        """계약서 원문 해시 계산"""
        contract_data = {
            'type': self.type.value,
            'seller_name': self.seller_name,
            'buyer_name': self.buyer_name,
            'property_address': self.property_address,
            'price_total': self.price_total,
            'deposit': self.deposit,
            'monthly_rent': self.monthly_rent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        contract_json = json.dumps(contract_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(contract_json.encode('utf-8')).hexdigest()
    
    def get_short_hash(self):
        """16자리 짧은 해시"""
        return self.doc_hash[:16] if self.doc_hash else None
    
    def to_dict(self):
        from datetime import datetime, date
        
        # 상태 계산 (DB 값이 없으면 자동 계산)
        computed_status = self.status.value if self.status else 'DRAFT'
        if not self.status and self.schedule:
            today = date.today()
            
            contract_date = self.schedule.get('contract_date')
            handover_date = self.schedule.get('handover_date')
            
            if contract_date and handover_date:
                try:
                    # ISO 형식 날짜 파싱
                    if 'T' in contract_date:
                        start_date = datetime.fromisoformat(contract_date.replace('Z', '')).date()
                    else:
                        start_date = datetime.strptime(contract_date, '%Y-%m-%d').date()
                    
                    if 'T' in handover_date:
                        end_date = datetime.fromisoformat(handover_date.replace('Z', '')).date()
                    else:
                        end_date = datetime.strptime(handover_date, '%Y-%m-%d').date()
                    
                    if today < start_date:
                        computed_status = 'DRAFT'
                    elif today > end_date:
                        computed_status = 'EXPIRED'
                    else:
                        computed_status = 'ACTIVE'
                except Exception as e:
                    print(f"Date parsing error: {e}")
                    computed_status = 'DRAFT'
        
        # 서명 정보 가져오기
        signatures = []
        if hasattr(self, 'signatures'):
            for sig in self.signatures:
                signatures.append({
                    'id': sig.id,
                    'role': sig.role.value,
                    'image_url': f'/api/contracts/{self.id}/signatures/{sig.id}.png',
                    'signed_at': sig.signed_at.isoformat() if sig.signed_at else None
                })
        
        return {
            'id': self.id,
            'type': self.type.value,
            'form_version': self.form_version,
            'status': computed_status,
            'computed_status': computed_status,
            'seller_name': self.seller_name,
            'seller_phone': self.seller_phone,
            'buyer_name': self.buyer_name,
            'buyer_phone': self.buyer_phone,
            'property_address': self.property_address,
            'unit': self.unit,
            # 타입별 금액 필드 (int 또는 None)
            'sale_price': int(self.sale_price) if self.sale_price is not None else None,
            'deposit': int(self.deposit) if self.deposit is not None else None,
            'monthly_rent': int(self.monthly_rent) if self.monthly_rent is not None else None,
            'monthly_payday': self.monthly_payday,
            # 날짜 필드 (ISO 형식 또는 None)
            'contract_date': self.contract_date.isoformat() if self.contract_date else None,
            'handover_date': self.handover_date.isoformat() if self.handover_date else None,
            # 호환성을 위한 기존 필드
            'price_total': self.price_total,
            # 기타 필드
            'mgmt_fee': self.mgmt_fee,
            'mgmt_note': self.mgmt_note,
            'schedule': self.schedule,
            'brokerage': self.brokerage,
            'attachments': self.attachments,
            'special_terms': self.special_terms,
            'doc_no': self.doc_no,
            'doc_hash': self.doc_hash,
            'short_hash': self.get_short_hash(),
            'signatures': signatures,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ContractSignature(db.Model):
    __tablename__ = 'contract_signatures'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    role = db.Column(db.Enum(SignatureRole), nullable=False)
    
    # 인증 정보
    auth_method = db.Column(db.Enum(AuthMethod))
    auth_ref = db.Column(db.String(128))  # 인증 참조번호
    
    # 서명 정보
    image_path = db.Column(db.Text, nullable=True)  # 서명 이미지 파일 경로
    signed_payload_hash = db.Column(db.String(64))  # 서명된 페이로드 해시
    ip = db.Column(db.String(45))  # IP 주소
    ua = db.Column(db.Text)        # User Agent
    
    # 타임스탬프
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    contract = db.relationship('Contract', backref=db.backref('signatures', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'role': self.role.value,
            'image_url': f'/api/contracts/{self.contract_id}/signatures/{self.id}.png' if self.image_path else None,
            'auth_method': self.auth_method.value if self.auth_method else None,
            'auth_ref': self.auth_ref,
            'signed_payload_hash': self.signed_payload_hash,
            'ip': self.ip,
            'ua': self.ua,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None
        }

class ContractEvent(db.Model):
    __tablename__ = 'contract_events'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    actor_id = db.Column(db.Integer)  # 사용자 ID (선택)
    event_type = db.Column(db.String(50), nullable=False)  # CREATED, UPDATED, SIGNED, etc.
    meta = db.Column(db.JSON)  # 이벤트 메타데이터
    event_hash = db.Column(db.String(64))  # 이벤트 해시
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계
    contract = db.relationship('Contract', backref=db.backref('events', lazy=True))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.event_hash:
            self.event_hash = self.calculate_event_hash()
    
    def calculate_event_hash(self):
        """이벤트 해시 계산"""
        event_data = {
            'contract_id': self.contract_id,
            'event_type': self.event_type,
            'meta': self.meta,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        event_json = json.dumps(event_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(event_json.encode('utf-8')).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'actor_id': self.actor_id,
            'event_type': self.event_type,
            'meta': self.meta,
            'event_hash': self.event_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Electronic Signature Models
class SignStatus(Enum):
    """서명 상태"""
    PENDING = "PENDING"      # 대기 중
    VIEWED = "VIEWED"        # 열람됨
    SIGNED = "SIGNED"        # 서명 완료
    EXPIRED = "EXPIRED"      # 만료됨
    CANCELED = "CANCELED"    # 취소됨


class SignRole(Enum):
    """서명자 역할"""
    SELLER = "SELLER"        # 매도인
    BUYER = "BUYER"          # 매수인
    LESSOR = "LESSOR"        # 임대인
    LESSEE = "LESSEE"        # 임차인
    BROKER = "BROKER"        # 중개인
    AGENT = "AGENT"          # 중개업자
    GUARANTOR = "GUARANTOR"  # 보증인


class SignRequest(db.Model):
    """서명 요청 모델"""
    __tablename__ = 'sign_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    role = db.Column(db.Enum(SignRole), nullable=False)
    
    # 서명자 정보
    signer_name = db.Column(db.String(100), nullable=False)
    signer_email = db.Column(db.String(255), nullable=False)
    signer_phone = db.Column(db.String(20), nullable=True)
    
    # 토큰 및 만료
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(SignStatus), default=SignStatus.PENDING, nullable=False)
    
    # 서명 정보
    signed_at = db.Column(db.DateTime, nullable=True)
    signature_image_path = db.Column(db.String(500), nullable=True)  # PNG 파일 경로
    
    # 메타데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 관계는 Contract 모델에서 정의됨
    
    @staticmethod
    def new_token():
        """새로운 서명 토큰 생성"""
        import secrets
        import string
        # 32자리 고엔트로피 토큰 생성
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @classmethod
    def create(cls, contract_id, role, signer_name, signer_email, signer_phone=None, ttl_days=7):
        """서명 요청 생성"""
        from datetime import timedelta
        token = cls.new_token()
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        
        return cls(
            contract_id=contract_id,
            role=role,
            signer_name=signer_name,
            signer_email=signer_email,
            signer_phone=signer_phone,
            token=token,
            expires_at=expires_at,
            status=SignStatus.PENDING
        )
    
    def is_expired(self):
        """만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """유효한 토큰인지 확인"""
        return not self.is_expired() and self.status in [SignStatus.PENDING, SignStatus.VIEWED]
    
    def mark_viewed(self):
        """열람 상태로 변경"""
        if self.status == SignStatus.PENDING:
            self.status = SignStatus.VIEWED
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def mark_signed(self, signature_image_path):
        """서명 완료로 변경"""
        if self.is_valid():
            self.status = SignStatus.SIGNED
            self.signed_at = datetime.utcnow()
            self.signature_image_path = signature_image_path
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def mark_expired(self):
        """만료 상태로 변경"""
        if self.status in [SignStatus.PENDING, SignStatus.VIEWED]:
            self.status = SignStatus.EXPIRED
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def mark_canceled(self):
        """취소 상태로 변경"""
        if self.status in [SignStatus.PENDING, SignStatus.VIEWED]:
            self.status = SignStatus.CANCELED
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_sign_url(self, base_url):
        """서명 URL 생성"""
        return f"{base_url}/sign/{self.token}"
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'role': self.role.value,
            'signer_name': self.signer_name,
            'signer_email': self.signer_email,
            'signer_phone': self.signer_phone,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'status': self.status.value,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'signature_image_path': self.signature_image_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f"<SignRequest(id={self.id}, contract_id={self.contract_id}, role={self.role.value}, status={self.status.value})>"
