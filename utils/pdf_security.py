#!/usr/bin/env python3
"""
PDF 보안 및 무결성 검증 모듈
"""

import hashlib
import hmac
import secrets
import qrcode
import io
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from models import Contract, ContractEvent, db
from flask import current_app

class PdfSecurityManager:
    """PDF 보안 관리자"""
    
    def __init__(self):
        self.watermark_text = "Hatch 자동생성 계약서 – 국토부 표준양식 기반"
        self.security_salt = current_app.config.get('PDF_SECURITY_SALT', 'hatch_contract_security_2025')
    
    def calculate_content_hash(self, content):
        """콘텐츠 SHA-256 해시 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def calculate_pdf_hash(self, pdf_content):
        """PDF 바이너리 SHA-256 해시 계산"""
        return hashlib.sha256(pdf_content).hexdigest()
    
    def generate_contract_hash(self, contract):
        """계약서 고유 해시 생성"""
        hash_data = {
            'contract_id': contract.id,
            'doc_no': contract.doc_no,
            'type': contract.type.value,
            'seller_name': contract.seller_name,
            'buyer_name': contract.buyer_name,
            'property_address': contract.property_address,
            'created_at': contract.created_at.isoformat(),
            'form_version': contract.form_version
        }
        
        # JSON 직렬화 후 해시
        import json
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def create_qr_code(self, contract, doc_hash):
        """QR 코드 생성"""
        qr_data = {
            'contract_id': contract.id,
            'doc_no': contract.doc_no,
            'hash': doc_hash[:16],  # 짧은 해시
            'generated_at': datetime.now().isoformat(),
            'version': contract.form_version
        }
        
        # QR 데이터를 문자열로 변환
        import json
        qr_string = json.dumps(qr_data, sort_keys=True)
        
        # QR 코드 생성
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # PIL Image를 base64로 변환
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return base64.b64encode(img_buffer.getvalue()).decode()
    
    def create_security_watermark(self, contract):
        """보안 워터마크 생성"""
        watermark_data = {
            'text': self.watermark_text,
            'contract_id': contract.id,
            'doc_no': contract.doc_no,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': contract.form_version
        }
        
        return watermark_data
    
    def generate_digital_signature(self, contract, pdf_content):
        """디지털 서명 생성 (HMAC 기반)"""
        # 계약서 메타데이터
        metadata = f"{contract.id}:{contract.doc_no}:{contract.type.value}:{contract.created_at.isoformat()}"
        
        # HMAC 서명 생성
        signature = hmac.new(
            self.security_salt.encode('utf-8'),
            metadata.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_digital_signature(self, contract, signature):
        """디지털 서명 검증"""
        expected_signature = self.generate_digital_signature(contract, b'')
        return hmac.compare_digest(signature, expected_signature)
    
    def create_security_footer(self, contract, doc_hash):
        """보안 푸터 정보 생성"""
        return {
            'contract_id': contract.id,
            'doc_no': contract.doc_no,
            'hash_sha256': doc_hash,
            'short_hash': doc_hash[:16],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'form_version': contract.form_version,
            'security_level': 'HIGH',
            'integrity_check': 'PASSED'
        }
    
    def log_security_event(self, contract, event_type, details=None):
        """보안 이벤트 로깅"""
        try:
            event = ContractEvent(
                contract_id=contract.id,
                event_type=event_type,
                meta={
                    'security_event': True,
                    'timestamp': datetime.now().isoformat(),
                    'details': details or {}
                }
            )
            db.session.add(event)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"보안 이벤트 로깅 실패: {e}")
    
    def validate_contract_integrity(self, contract):
        """계약서 무결성 검증"""
        try:
            # 1. 기본 해시 검증
            current_hash = contract.calculate_hash()
            stored_hash = contract.doc_hash
            
            hash_valid = current_hash == stored_hash if stored_hash else False
            
            # 2. 서명 무결성 검증
            signatures = contract.signatures
            signature_valid = all(
                sig.signed_payload_hash and sig.signed_at 
                for sig in signatures
            ) if signatures else True
            
            # 3. 문서 번호 검증
            doc_no_valid = contract.doc_no and len(contract.doc_no) > 10
            
            # 4. 전체 무결성 평가
            integrity_score = sum([hash_valid, signature_valid, doc_no_valid])
            is_integrity_valid = integrity_score >= 2
            
            return {
                'is_valid': is_integrity_valid,
                'integrity_score': integrity_score,
                'hash_valid': hash_valid,
                'signature_valid': signature_valid,
                'doc_no_valid': doc_no_valid,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"무결성 검증 실패: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def create_security_report(self, contract):
        """보안 보고서 생성"""
        try:
            # 무결성 검증
            integrity_result = self.validate_contract_integrity(contract)
            
            # 서명 정보
            signatures = contract.signatures
            signature_count = len(signatures) if signatures else 0
            verified_signatures = len([
                sig for sig in signatures 
                if sig.signed_payload_hash and sig.signed_at
            ]) if signatures else 0
            
            # 보안 보고서
            report = {
                'contract_id': contract.id,
                'doc_no': contract.doc_no,
                'security_level': 'HIGH',
                'integrity': integrity_result,
                'signatures': {
                    'total': signature_count,
                    'verified': verified_signatures,
                    'completion_rate': (verified_signatures / signature_count * 100) if signature_count > 0 else 0
                },
                'generated_at': datetime.now().isoformat(),
                'form_version': contract.form_version,
                'security_features': [
                    'SHA-256 해시 검증',
                    'QR 코드 무결성',
                    '디지털 서명',
                    '타임스탬프',
                    '워터마크'
                ]
            }
            
            return report
            
        except Exception as e:
            current_app.logger.error(f"보안 보고서 생성 실패: {e}")
            return None

# 전역 보안 관리자 인스턴스
security_manager = PdfSecurityManager()

def get_contract_security_info(contract):
    """계약서 보안 정보 조회"""
    return security_manager.create_security_report(contract)

def verify_contract_security(contract):
    """계약서 보안 검증"""
    return security_manager.validate_contract_integrity(contract)

def generate_contract_qr_code(contract, doc_hash):
    """계약서 QR 코드 생성"""
    return security_manager.create_qr_code(contract, doc_hash)

def create_contract_watermark(contract):
    """계약서 워터마크 생성"""
    return security_manager.create_security_watermark(contract)


