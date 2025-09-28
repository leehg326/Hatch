# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, make_response, current_app
from datetime import datetime, date, timedelta
from models import db, Contract, User
from security import verify_jwt_token
import json

bp = Blueprint('contracts', __name__, url_prefix='/api/contracts')

def get_current_user():
    """JWT token에서 현재 사용자 정보를 가져옵니다."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        payload = verify_jwt_token(token)
        if payload:
            user_id = payload.get('user_id')
            return User.query.get(user_id)
    except Exception as e:
        print(f"Token verification error: {e}")
    
    return None

@bp.route('', methods=['POST'])
def create_contract():
    """새로운 계약서를 생성합니다."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '인증이 필요합니다'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다'}), 400
        
        contract_type = data.get('contract_type', 'rental')
        
        if contract_type == 'sale':
            # 매매계약서 생성
            return create_sale_contract(user, data)
        else:
            # 임대차/전세/월세/반전세 계약서 생성
            return create_rental_contract(user, data)
            
    except Exception as e:
        print(f"Contract creation error: {e}")
        return jsonify({'error': '계약서 생성 중 오류가 발생했습니다'}), 500

def create_sale_contract(user, data):
    """매매계약서를 생성합니다."""
    try:
        # 필수 필드 검증
        required_fields = ['buyer_name', 'buyer_phone', 'seller_name', 'seller_phone', 'property_address', 'sale_price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}는 필수 항목입니다'}), 400
        
        # 자동 계산된 금액들
        sale_price = int(data['sale_price'])
        contract_deposit = data.get('contract_deposit', int(sale_price * 0.1))  # 10%
        intermediate_payment = data.get('intermediate_payment', int(sale_price * 0.4))  # 40%
        final_payment = data.get('final_payment', int(sale_price * 0.5))  # 50%
        
        # 자동 설정된 날짜들
        today = date.today()
        contract_date = today
        final_payment_date = today + timedelta(days=60)  # +60일
        delivery_date = final_payment_date  # 잔금일과 동일
        
        # 계약서 생성
        contract = Contract(
            user_id=user.id,
            contract_type='sale',
            buyer_name=data['buyer_name'],
            buyer_phone=data['buyer_phone'],
            seller_name=data['seller_name'],
            seller_phone=data['seller_phone'],
            property_address=data['property_address'],
            sale_price=sale_price,
            contract_deposit=contract_deposit,
            intermediate_payment=intermediate_payment,
            final_payment=final_payment,
            contract_date=contract_date,
            final_payment_date=final_payment_date,
            delivery_date=delivery_date,
            memo=data.get('memo', '')
        )
        
        db.session.add(contract)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contract_id': contract.id,
            'message': '매매계약서가 성공적으로 생성되었습니다'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Sale contract creation error: {e}")
        return jsonify({'error': '매매계약서 생성 중 오류가 발생했습니다'}), 500

def create_rental_contract(user, data):
    """임대차/전세/월세/반전세 계약서를 생성합니다."""
    try:
        contract_type = data.get('contract_type', 'rental')
        
        # 필수 필드 검증
        required_fields = ['customer_name', 'customer_phone', 'property_address', 'price', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}는 필수 항목입니다'}), 400
        
        # 월세/반전세의 경우 보증금 필수
        if contract_type in ['monthly', 'reverse'] and not data.get('deposit'):
            return jsonify({'error': '보증금은 필수 항목입니다'}), 400
        
        # 계약서 생성
        contract = Contract(
            user_id=user.id,
            contract_type=contract_type,
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            property_address=data['property_address'],
            price=int(data['price']),
            deposit=int(data.get('deposit', 0)) if contract_type in ['monthly', 'reverse'] else None,
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            memo=data.get('memo', ''),
            signature_data=data.get('signature_data', '')
        )
        
        db.session.add(contract)
        db.session.commit()
        
        contract_type_labels = {
            'rental': '임대차계약서',
            'jeonse': '전세계약서',
            'monthly': '월세계약서',
            'reverse': '반전세계약서'
        }
        
        return jsonify({
            'success': True,
            'id': contract.id,
            'message': f'{contract_type_labels.get(contract_type, "계약서")}가 성공적으로 생성되었습니다'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Contract creation error: {e}")
        return jsonify({'error': '계약서 생성 중 오류가 발생했습니다'}), 500

@bp.route('', methods=['GET'])
def get_contracts():
    """사용자의 계약서 목록을 조회합니다."""
    try:
        user = get_current_user()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_query = request.args.get('q', '')
        contract_type = request.args.get('type', '')
        
        # 계약서 조회 - 인증된 사용자만 해당 사용자의 계약서, 아니면 모든 계약서 (개발용)
        if user:
            query = Contract.query.filter_by(user_id=user.id)
        else:
            # 개발용: 인증되지 않은 경우 모든 계약서 조회
            query = Contract.query
        
        # 타입 필터링
        if contract_type and contract_type in ['sale', 'rental']:
            query = query.filter_by(contract_type=contract_type)
        
        if search_query:
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Contract.customer_name.contains(search_query),
                    Contract.buyer_name.contains(search_query),
                    Contract.seller_name.contains(search_query),
                    Contract.property_address.contains(search_query)
                )
            )
        
        query = query.order_by(Contract.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        contracts = [contract.to_dict() for contract in pagination.items] if pagination.items else []
        
        return jsonify({
            'contracts': contracts,
            'pages': pagination.pages or 1,
            'current_page': page,
            'total': pagination.total or 0
        }), 200
        
    except Exception as e:
        print(f"Get contracts error: {e}")
        return jsonify({'error': '계약서 목록 조회 중 오류가 발생했습니다'}), 500

@bp.route('/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """특정 계약서를 조회합니다."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '인증이 필요합니다'}), 401
        
        contract = Contract.query.filter_by(id=contract_id, user_id=user.id).first()
        if not contract:
            return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404
        
        return jsonify({
            'contract': contract.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Get contract error: {e}")
        return jsonify({'error': '계약서 조회 중 오류가 발생했습니다'}), 500

@bp.route('/<int:contract_id>/pdf', methods=['GET'])
def get_contract_pdf(contract_id):
    """계약서 PDF를 생성하고 반환합니다."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': '인증이 필요합니다'}), 401
        
        contract = Contract.query.filter_by(id=contract_id, user_id=user.id).first()
        if not contract:
            return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404
        
        # PDF 생성
        from pdf_generator import ContractPDFGenerator
        pdf_generator = ContractPDFGenerator()
        
        if contract.contract_type == 'sale':
            pdf_data = pdf_generator.generate_sale_contract_pdf(contract)
        else:
            pdf_data = pdf_generator.generate_rental_contract_pdf(contract)
        
        # PDF 응답 생성
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=contract_{contract_id}.pdf'
        
        return response
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({'error': 'PDF 생성 중 오류가 발생했습니다'}), 500