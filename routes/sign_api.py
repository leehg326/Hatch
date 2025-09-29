#!/usr/bin/env python3
"""
전자서명 API 라우터 - 링크형 전자서명 시스템
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import os
import base64
import uuid
from models import Contract, db
from models import SignRequest, SignRole, SignStatus
from services.notifier import send_email, send_sms

# API 블루프린트
sign_api_bp = Blueprint('sign_api', __name__, url_prefix='/api/sign')


@sign_api_bp.route('/requests', methods=['POST'])
def create_sign_requests():
    """서명 요청 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data or 'contract_id' not in data or 'signers' not in data:
            return jsonify({'error': '필수 필드가 누락되었습니다'}), 400
        
        contract_id = data['contract_id']
        signers = data['signers']
        
        # 계약서 존재 확인
        contract = Contract.query.get(contract_id)
        if not contract:
            return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404
        
        # 서명자 데이터 검증
        if not isinstance(signers, list) or len(signers) == 0:
            return jsonify({'error': '서명자 정보가 필요합니다'}), 400
        
        created_requests = []
        sign_urls = []
        
        for signer_data in signers:
            # 필수 필드 검증
            required_fields = ['role', 'name', 'email']
            for field in required_fields:
                if field not in signer_data:
                    return jsonify({'error': f'{field} 필드가 필요합니다'}), 400
            
            # 역할 검증
            try:
                role = SignRole(signer_data['role'])
            except ValueError:
                return jsonify({'error': f'유효하지 않은 역할: {signer_data["role"]}'}), 400
            
            # 서명 요청 생성
            sign_request = SignRequest.create(
                contract_id=contract_id,
                role=role,
                signer_name=signer_data['name'],
                signer_email=signer_data['email'],
                signer_phone=signer_data.get('phone'),
                ttl_days=7  # 기본 7일
            )
            
            db.session.add(sign_request)
            created_requests.append(sign_request)
        
        # 데이터베이스 커밋
        db.session.commit()
        
        # 각 서명자에게 URL 생성 및 발송
        base_url = current_app.config.get('APP_BASE_URL', 'http://127.0.0.1:5000')
        
        for sign_request in created_requests:
            sign_url = sign_request.get_sign_url(base_url)
            sign_urls.append({
                'id': sign_request.id,
                'role': sign_request.role.value,
                'signer_name': sign_request.signer_name,
                'signer_email': sign_request.signer_email,
                'sign_url': sign_url,
                'expires_at': sign_request.expires_at.isoformat()
            })
            
            # 이메일 발송 (더미)
            try:
                send_email(
                    to=sign_request.signer_email,
                    subject=f"[전자서명] {contract.type.value}계약서 서명 요청",
                    html=f"""
                    <h2>전자서명 요청</h2>
                    <p>안녕하세요, {sign_request.signer_name}님.</p>
                    <p>계약서 전자서명을 요청드립니다.</p>
                    <p><strong>계약서 ID:</strong> {contract.id}</p>
                    <p><strong>서명자 역할:</strong> {sign_request.role.value}</p>
                    <p><strong>만료일:</strong> {sign_request.expires_at.strftime('%Y-%m-%d %H:%M')}</p>
                    <p><a href="{sign_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">서명하기</a></p>
                    <p>위 링크를 클릭하여 서명을 완료해주세요.</p>
                    """
                )
            except Exception as e:
                current_app.logger.error(f"이메일 발송 실패: {e}")
            
            # SMS 발송 (더미)
            if sign_request.signer_phone:
                try:
                    send_sms(
                        phone=sign_request.signer_phone,
                        text=f"[전자서명] {contract.type.value}계약서 서명 요청이 도착했습니다. {sign_url}"
                    )
                except Exception as e:
                    current_app.logger.error(f"SMS 발송 실패: {e}")
        
        return jsonify({
            'success': True,
            'message': f'{len(created_requests)}개의 서명 요청이 생성되었습니다',
            'sign_requests': sign_urls
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"서명 요청 생성 실패: {e}")
        return jsonify({'error': '서명 요청 생성 중 오류가 발생했습니다'}), 500


@sign_api_bp.route('/<token>', methods=['GET'])
def get_sign_request(token):
    """서명 요청 조회"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return jsonify({'error': '서명 요청을 찾을 수 없습니다'}), 404
        
        if sign_request.is_expired():
            sign_request.mark_expired()
            db.session.commit()
            return jsonify({'error': '만료된 서명 요청입니다'}), 410
        
        # 최초 열람 시 상태 변경
        if sign_request.status == SignStatus.PENDING:
            sign_request.mark_viewed()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'sign_request': sign_request.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"서명 요청 조회 실패: {e}")
        return jsonify({'error': '서명 요청 조회 중 오류가 발생했습니다'}), 500


@sign_api_bp.route('/<token>', methods=['POST'])
def submit_signature(token):
    """서명 제출"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return jsonify({'error': '서명 요청을 찾을 수 없습니다'}), 404
        
        if sign_request.is_expired():
            sign_request.mark_expired()
            db.session.commit()
            return jsonify({'error': '만료된 서명 요청입니다'}), 410
        
        if sign_request.status == SignStatus.SIGNED:
            return jsonify({'error': '이미 서명이 완료되었습니다'}), 400
        
        # 서명 데이터 처리
        data = request.get_json()
        if not data or 'signature' not in data:
            return jsonify({'error': '서명 데이터가 필요합니다'}), 400
        
        signature_data = data['signature']
        
        # DataURL에서 이미지 데이터 추출
        if signature_data.startswith('data:image/png;base64,'):
            signature_data = signature_data.split(',')[1]
        
        try:
            # Base64 디코딩
            signature_bytes = base64.b64decode(signature_data)
        except Exception as e:
            return jsonify({'error': '유효하지 않은 서명 데이터입니다'}), 400
        
        # 서명 이미지 저장
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'signatures', str(sign_request.contract_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{sign_request.role.value}_{sign_request.id}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(signature_bytes)
        
        # 상대 경로로 저장
        relative_path = f"uploads/signatures/{sign_request.contract_id}/{filename}"
        
        # 서명 완료 처리
        if sign_request.mark_signed(relative_path):
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '서명이 완료되었습니다',
                'sign_request': sign_request.to_dict()
            }), 200
        else:
            return jsonify({'error': '서명 처리 중 오류가 발생했습니다'}), 500
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"서명 제출 실패: {e}")
        return jsonify({'error': '서명 제출 중 오류가 발생했습니다'}), 500


@sign_api_bp.route('/<token>/status', methods=['GET'])
def get_sign_status(token):
    """서명 상태 조회"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return jsonify({'error': '서명 요청을 찾을 수 없습니다'}), 404
        
        return jsonify({
            'success': True,
            'status': sign_request.status.value,
            'is_expired': sign_request.is_expired(),
            'is_valid': sign_request.is_valid(),
            'signed_at': sign_request.signed_at.isoformat() if sign_request.signed_at else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"서명 상태 조회 실패: {e}")
        return jsonify({'error': '서명 상태 조회 중 오류가 발생했습니다'}), 500


@sign_api_bp.route('/contracts/<int:contract_id>/requests', methods=['GET'])
def get_contract_sign_requests(contract_id):
    """계약서의 모든 서명 요청 조회"""
    try:
        contract = Contract.query.get(contract_id)
        if not contract:
            return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404
        
        sign_requests = SignRequest.query.filter_by(contract_id=contract_id).all()
        
        return jsonify({
            'success': True,
            'sign_requests': [req.to_dict() for req in sign_requests]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"계약서 서명 요청 조회 실패: {e}")
        return jsonify({'error': '서명 요청 조회 중 오류가 발생했습니다'}), 500
