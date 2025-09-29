#!/usr/bin/env python3
"""
알림 서비스 - 이메일/SMS 발송 (더미 구현)
"""

from flask import current_app
import logging

logger = logging.getLogger(__name__)


def send_email(to, subject, html, text=None):
    """
    이메일 발송 (더미 구현)
    
    Args:
        to (str): 수신자 이메일
        subject (str): 제목
        html (str): HTML 내용
        text (str, optional): 텍스트 내용
    """
    try:
        # 실제 서비스에서는 SendGrid, AWS SES, SMTP 등을 사용
        logger.info(f"[이메일 발송] 수신자: {to}, 제목: {subject}")
        logger.info(f"[이메일 내용] {html[:100]}...")
        
        # 더미 성공 응답
        return {
            'success': True,
            'message_id': f'dummy_email_{to}_{subject}',
            'status': 'sent'
        }
        
    except Exception as e:
        logger.error(f"이메일 발송 실패: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def send_sms(phone, text):
    """
    SMS 발송 (더미 구현)
    
    Args:
        phone (str): 수신자 전화번호
        text (str): 메시지 내용
    """
    try:
        # 실제 서비스에서는 Twilio, AWS SNS, 카카오 비즈메시지 등을 사용
        logger.info(f"[SMS 발송] 수신자: {phone}, 내용: {text}")
        
        # 더미 성공 응답
        return {
            'success': True,
            'message_id': f'dummy_sms_{phone}',
            'status': 'sent'
        }
        
    except Exception as e:
        logger.error(f"SMS 발송 실패: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def send_signature_request_notification(sign_request, contract, sign_url):
    """
    서명 요청 알림 발송
    
    Args:
        sign_request: 서명 요청 객체
        contract: 계약서 객체
        sign_url: 서명 URL
    """
    try:
        # 이메일 발송
        email_result = send_email(
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
        
        # SMS 발송 (전화번호가 있는 경우)
        sms_result = None
        if sign_request.signer_phone:
            sms_result = send_sms(
                phone=sign_request.signer_phone,
                text=f"[전자서명] {contract.type.value}계약서 서명 요청이 도착했습니다. {sign_url}"
            )
        
        return {
            'email': email_result,
            'sms': sms_result
        }
        
    except Exception as e:
        logger.error(f"서명 요청 알림 발송 실패: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def send_signature_completion_notification(sign_request, contract):
    """
    서명 완료 알림 발송
    
    Args:
        sign_request: 서명 요청 객체
        contract: 계약서 객체
    """
    try:
        # 관리자에게 서명 완료 알림
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@example.com')
        
        email_result = send_email(
            to=admin_email,
            subject=f"[서명 완료] {contract.type.value}계약서 서명 완료",
            html=f"""
            <h2>서명 완료 알림</h2>
            <p>계약서 서명이 완료되었습니다.</p>
            <p><strong>계약서 ID:</strong> {contract.id}</p>
            <p><strong>서명자:</strong> {sign_request.signer_name}</p>
            <p><strong>역할:</strong> {sign_request.role.value}</p>
            <p><strong>서명 완료일:</strong> {sign_request.signed_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
        )
        
        return email_result
        
    except Exception as e:
        logger.error(f"서명 완료 알림 발송 실패: {e}")
        return {
            'success': False,
            'error': str(e)
        }
