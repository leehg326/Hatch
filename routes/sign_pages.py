#!/usr/bin/env python3
"""
전자서명 페이지 라우터 - 서명 페이지 및 만료 페이지
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import SignRequest, SignStatus
from models import db

# 페이지 블루프린트
sign_pages_bp = Blueprint('sign_pages', __name__)


@sign_pages_bp.route('/sign/<token>')
def sign_page(token):
    """서명 페이지"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return render_template('sign/not_found.html'), 404
        
        # 만료 확인
        if sign_request.is_expired():
            sign_request.mark_expired()
            db.session.commit()
            return redirect(url_for('sign_pages.expired_page', token=token))
        
        # 이미 서명 완료된 경우
        if sign_request.status == SignStatus.SIGNED:
            return render_template('sign/already_signed.html', 
                                 sign_request=sign_request)
        
        # 최초 열람 시 상태 변경
        if sign_request.status == SignStatus.PENDING:
            sign_request.mark_viewed()
            db.session.commit()
        
        # 계약서 정보 로드
        contract = sign_request.contract
        
        return render_template('sign/sign.html', 
                             sign_request=sign_request,
                             contract=contract)
        
    except Exception as e:
        current_app.logger.error(f"서명 페이지 로드 실패: {e}")
        return render_template('sign/error.html', error=str(e)), 500


@sign_pages_bp.route('/sign/<token>/expired')
def expired_page(token):
    """만료 페이지"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return render_template('sign/not_found.html'), 404
        
        return render_template('sign/expired.html', 
                             sign_request=sign_request)
        
    except Exception as e:
        current_app.logger.error(f"만료 페이지 로드 실패: {e}")
        return render_template('sign/error.html', error=str(e)), 500


@sign_pages_bp.route('/sign/<token>/success')
def success_page(token):
    """서명 완료 페이지"""
    try:
        sign_request = SignRequest.query.filter_by(token=token).first()
        
        if not sign_request:
            return render_template('sign/not_found.html'), 404
        
        if sign_request.status != SignStatus.SIGNED:
            return redirect(url_for('sign_pages.sign_page', token=token))
        
        return render_template('sign/success.html', 
                             sign_request=sign_request)
        
    except Exception as e:
        current_app.logger.error(f"성공 페이지 로드 실패: {e}")
        return render_template('sign/error.html', error=str(e)), 500
