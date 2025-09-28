#!/usr/bin/env python3
"""
PDF 생성 라우트 - WeasyPrint 기반 계약서 PDF 생성
"""

from flask import Blueprint, render_template, request, send_file, jsonify, current_app
from models import Contract, ContractSignature, ContractEvent, db
from datetime import datetime
import hashlib
import qrcode
import io
import os
import base64
from PIL import Image
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from utils.pdf_signature import integrate_contract_signatures, verify_contract_signatures
from utils.pdf_security import (
    security_manager, 
    get_contract_security_info, 
    verify_contract_security,
    generate_contract_qr_code,
    create_contract_watermark
)

# PDF 생성용 Blueprint
pdf_bp = Blueprint('pdf', __name__, url_prefix='/api')

def create_qr_code(contract_id, doc_hash):
    """QR 코드 생성"""
    qr_data = f"CONTRACT_ID:{contract_id}|HASH:{doc_hash[:16]}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # PIL Image를 base64로 변환
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return base64.b64encode(img_buffer.getvalue()).decode()

def calculate_pdf_hash(pdf_content):
    """PDF 내용의 SHA-256 해시 계산"""
    return hashlib.sha256(pdf_content).hexdigest()

def generate_contract_pdf(contract, mode='inline'):
    """계약서 PDF 생성 (서명 통합 및 보안 기능 포함)"""
    try:
        # 계약 유형에 따른 템플릿 선택
        template_map = {
            'SALE': 'contracts/sale.html',
            'JEONSE': 'contracts/jeonse.html', 
            'WOLSE': 'contracts/wolse.html'
        }
        
        template_name = template_map.get(contract.type.value, 'contracts/sale.html')
        
        # 서명 정보 로드
        signatures = ContractSignature.query.filter_by(contract_id=contract.id).all()
        contract.signatures = signatures
        
        # 보안 정보 생성
        doc_hash = contract.doc_hash or contract.calculate_hash()
        qr_code_data = generate_contract_qr_code(contract, doc_hash)
        watermark_data = create_contract_watermark(contract)
        
        # 템플릿 렌더링
        html_content = render_template(
            template_name,
            contract=contract,
            qr_code_data=qr_code_data,
            watermark_data=watermark_data,
            current_time=datetime.now()
        )
        
        # CSS 파일 경로
        css_path = os.path.join(current_app.static_folder, 'css', 'print.css')
        
        # 서명 통합 PDF 생성
        pdf_content = integrate_contract_signatures(contract, html_content, css_path)
        
        # PDF 해시 계산 및 저장
        pdf_hash = calculate_pdf_hash(pdf_content)
        contract.pdf_sha256 = pdf_hash
        db.session.commit()
        
        # 보안 이벤트 로깅
        security_manager.log_security_event(
            contract, 
            'PDF_GENERATED_SECURE',
            {
                'mode': mode,
                'pdf_hash': pdf_hash,
                'signature_count': len(signatures),
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
        )
        
        return pdf_content
        
    except Exception as e:
        current_app.logger.error(f"PDF 생성 오류: {str(e)}")
        raise e

@pdf_bp.route('/contracts/<int:contract_id>/pdf', methods=['GET'])
def get_contract_pdf(contract_id):
    """계약서 PDF 생성 및 반환"""
    try:
        # 계약서 조회
        contract = Contract.query.get_or_404(contract_id)
        
        # 권한 확인 (사용자가 해당 계약서의 소유자인지 확인)
        # 실제 구현에서는 인증 로직 추가 필요
        
        # PDF 생성
        pdf_content = generate_contract_pdf(contract)
        
        # 모드에 따른 응답 설정
        mode = request.args.get('mode', 'inline')
        
        if mode == 'download':
            # 다운로드용 응답
            filename = f"contract_{contract_id}_{contract.type.value.lower()}.pdf"
            return send_file(
                io.BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            # 미리보기용 응답
            return send_file(
                io.BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=False
            )
            
    except Exception as e:
        current_app.logger.error(f"PDF 생성 실패: {str(e)}")
        return jsonify({
            'error': 'PDF 생성 중 오류가 발생했습니다',
            'details': str(e)
        }), 500

@pdf_bp.route('/contracts/<int:contract_id>/pdf/info', methods=['GET'])
def get_pdf_info(contract_id):
    """PDF 정보 조회 (해시, 생성일 등)"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        return jsonify({
            'contract_id': contract.id,
            'doc_no': contract.doc_no,
            'doc_hash': contract.doc_hash,
            'pdf_hash': getattr(contract, 'pdf_sha256', None),
            'created_at': contract.created_at.isoformat(),
            'updated_at': contract.updated_at.isoformat(),
            'form_version': contract.form_version
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/pdf/verify', methods=['POST'])
def verify_pdf_integrity(contract_id):
    """PDF 무결성 검증"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        # 현재 PDF 해시 계산
        pdf_content = generate_contract_pdf(contract)
        current_hash = calculate_pdf_hash(pdf_content)
        
        # 저장된 해시와 비교
        stored_hash = getattr(contract, 'pdf_sha256', None)
        
        is_valid = stored_hash == current_hash if stored_hash else False
        
        return jsonify({
            'contract_id': contract.id,
            'is_valid': is_valid,
            'current_hash': current_hash,
            'stored_hash': stored_hash,
            'verified_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/signatures/<int:signature_id>.png', methods=['GET'])
def get_signature_image(contract_id, signature_id):
    """서명 이미지 반환"""
    try:
        signature = ContractSignature.query.filter_by(
            contract_id=contract_id,
            id=signature_id
        ).first_or_404()
        
        if not signature.image_path or not os.path.exists(signature.image_path):
            return jsonify({'error': '서명 이미지를 찾을 수 없습니다'}), 404
        
        return send_file(
            signature.image_path,
            mimetype='image/png',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/events', methods=['GET'])
def get_contract_events(contract_id):
    """계약서 이벤트 로그 조회"""
    try:
        events = ContractEvent.query.filter_by(contract_id=contract_id)\
            .order_by(ContractEvent.created_at.desc()).all()
        
        return jsonify({
            'contract_id': contract_id,
            'events': [event.to_dict() for event in events]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/security', methods=['GET'])
def get_contract_security(contract_id):
    """계약서 보안 정보 조회"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        security_info = get_contract_security_info(contract)
        
        if not security_info:
            return jsonify({'error': '보안 정보를 생성할 수 없습니다'}), 500
        
        return jsonify(security_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/security/verify', methods=['POST'])
def verify_contract_security_endpoint(contract_id):
    """계약서 보안 검증"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        security_result = verify_contract_security(contract)
        
        return jsonify(security_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_bp.route('/contracts/<int:contract_id>/signatures/verify', methods=['POST'])
def verify_contract_signatures_endpoint(contract_id):
    """계약서 서명 검증"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        signature_result = verify_contract_signatures(contract)
        
        return jsonify(signature_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PDF 생성 헬퍼 함수들
def create_contract_event(contract_id, event_type, meta=None):
    """계약서 이벤트 생성"""
    event = ContractEvent(
        contract_id=contract_id,
        event_type=event_type,
        meta=meta or {}
    )
    db.session.add(event)
    return event

def update_contract_hash(contract):
    """계약서 해시 업데이트"""
    contract.doc_hash = contract.calculate_hash()
    db.session.commit()
    return contract.doc_hash

# 에러 핸들러
@pdf_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404

@pdf_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다'}), 500
