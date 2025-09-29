# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, date, timedelta
from models import db, Contract, ContractType, ContractStatus, ContractEvent
from pdf.standard_contract import StandardContractPDF
from validators import validate_contract_payload, to_int_safe
import json
import math
import io
from sqlalchemy import or_, and_

bp = Blueprint('contracts_api', __name__, url_prefix='/api')

# 정책 상수
POLICY_CONSTANTS = {
    'SALE': {
        'contract_ratio': 0.10,    # 계약금 10%
        'middle_ratio': 0.40,      # 중도금 40%
        'balance_ratio': 0.50,     # 잔금 50%
        'contract_days': 0,        # 계약일
        'middle_days': 30,         # 중도금일
        'balance_days': 60,        # 잔금일
        'transfer_days': 60        # 인도일
    },
    'JEONSE': {
        'deposit_ratio': 1.0,      # 보증금 100%
        'balance_days': 60,        # 잔금일
        'transfer_days': 60        # 인도일
    },
    'WOLSE': {
        'balance_days': 0,         # 보증금일
        'transfer_days': 0         # 인도일
    },
    'BANJEONSE': {
        'balance_days': 0,         # 보증금일
        'transfer_days': 0         # 인도일
    }
}


def calculate_contract_amounts(contract_type, data):
    """계약 금액 자동 계산"""
    amounts = {}
    today = date.today()
    
    if contract_type == 'SALE':
        # 안전한 정수 변환
        price_total, _ = to_int_safe(data.get('price_total', 0), 'price_total')
        policy = POLICY_CONSTANTS['SALE']
        
        amounts = {
            'price_total': price_total,
            'contract_amount': math.floor(price_total * policy['contract_ratio']),
            'middle_amount': math.floor(price_total * policy['middle_ratio']),
            'balance_amount': math.floor(price_total * policy['balance_ratio']),
            'schedule': {
                'contract_date': today.isoformat(),
                'middle_date': (today + timedelta(days=policy['middle_days'])).isoformat(),
                'balance_date': (today + timedelta(days=policy['balance_days'])).isoformat(),
                'transfer_date': (today + timedelta(days=policy['transfer_days'])).isoformat()
            }
        }
    
    elif contract_type == 'JEONSE':
        # 안전한 정수 변환
        deposit, _ = to_int_safe(data.get('deposit', 0), 'deposit')
        policy = POLICY_CONSTANTS['JEONSE']
        
        amounts = {
            'deposit': deposit,
            'schedule': {
                'contract_date': today.isoformat(),
                'balance_date': (today + timedelta(days=policy['balance_days'])).isoformat(),
                'transfer_date': (today + timedelta(days=policy['transfer_days'])).isoformat()
            }
        }
    
    elif contract_type in ['WOLSE', 'BANJEONSE']:
        # 안전한 정수 변환
        deposit, _ = to_int_safe(data.get('deposit', 0), 'deposit')
        monthly_rent, _ = to_int_safe(data.get('monthly_rent', 0), 'monthly_rent')
        monthly_payday = int(data.get('monthly_payday', 1))
        
        amounts = {
            'deposit': deposit,
            'monthly_rent': monthly_rent,
            'monthly_payday': monthly_payday,
            'schedule': {
                'contract_date': today.isoformat(),
                'balance_date': today.isoformat(),
                'transfer_date': today.isoformat()
            }
        }
    
    return amounts

def validate_contract_request(payload):
    """계약서 요청 validation"""
    import re
    errors = {}
    
    # 1. 기본 필수 필드 검증
    if not payload.get('type'):
        errors['type'] = '계약 유형은 필수입니다'
    elif payload['type'] not in ['SALE', 'JEONSE', 'WOLSE']:
        errors['type'] = '계약 유형은 SALE, JEONSE, WOLSE 중 하나여야 합니다'
    
    if not payload.get('property_address_full'):
        errors['property_address_full'] = '부동산 주소는 필수입니다'
    
    # 2. parties 검증
    parties = payload.get('parties', [])
    if not parties or len(parties) < 2:
        errors['parties'] = 'SELLER와 BUYER 정보가 필요합니다'
    else:
        roles = [p.get('role') for p in parties]
        if 'SELLER' not in roles or 'BUYER' not in roles:
            errors['parties'] = 'SELLER와 BUYER 역할이 모두 필요합니다'
        
        for i, party in enumerate(parties):
            if not party.get('name'):
                errors[f'parties[{i}].name'] = '이름은 필수입니다'
            if not party.get('phone'):
                errors[f'parties[{i}].phone'] = '전화번호는 필수입니다'
            elif not re.match(r'^[\d\-\s]+$', party.get('phone', '')):
                errors[f'parties[{i}].phone'] = '올바른 전화번호 형식이 아닙니다'
    
    # 3. 타입별 필수/금지 필드 검증
    contract_type = payload.get('type')
    if contract_type == 'SALE':
        # 매매: sale_price 필수, deposit/monthly_rent 금지
        if not payload.get('sale_price'):
            errors['sale_price'] = '매매가격은 필수입니다'
        elif not isinstance(payload.get('sale_price'), (int, float)) or payload.get('sale_price') <= 0:
            errors['sale_price'] = '매매가격은 0보다 큰 숫자여야 합니다'
        
        # 금지 필드 검증
        if 'deposit' in payload:
            errors['deposit'] = '매매 계약에서는 보증금을 입력할 수 없습니다'
        if 'monthly_rent' in payload:
            errors['monthly_rent'] = '매매 계약에서는 월세를 입력할 수 없습니다'
    
    elif contract_type == 'JEONSE':
        # 전세: deposit 필수, sale_price/monthly_rent 금지
        if not payload.get('deposit'):
            errors['deposit'] = '전세보증금은 필수입니다'
        elif not isinstance(payload.get('deposit'), (int, float)) or payload.get('deposit') <= 0:
            errors['deposit'] = '전세보증금은 0보다 큰 숫자여야 합니다'
        
        # 금지 필드 검증
        if 'sale_price' in payload:
            errors['sale_price'] = '전세 계약에서는 매매가격을 입력할 수 없습니다'
        if 'monthly_rent' in payload:
            errors['monthly_rent'] = '전세 계약에서는 월세를 입력할 수 없습니다'
    
    elif contract_type == 'WOLSE':
        # 월세: deposit, monthly_rent 필수, sale_price 금지
        if not payload.get('deposit'):
            errors['deposit'] = '보증금은 필수입니다'
        elif not isinstance(payload.get('deposit'), (int, float)) or payload.get('deposit') <= 0:
            errors['deposit'] = '보증금은 0보다 큰 숫자여야 합니다'
        
        if not payload.get('monthly_rent'):
            errors['monthly_rent'] = '월세는 필수입니다'
        elif not isinstance(payload.get('monthly_rent'), (int, float)) or payload.get('monthly_rent') <= 0:
            errors['monthly_rent'] = '월세는 0보다 큰 숫자여야 합니다'
        
        # 금지 필드 검증
        if 'sale_price' in payload:
            errors['sale_price'] = '월세 계약에서는 매매가격을 입력할 수 없습니다'
    
    # 4. 날짜 검증
    for date_field in ['contract_date', 'handover_date']:
        if payload.get(date_field):
            try:
                from datetime import datetime
                if isinstance(payload[date_field], str):
                    datetime.fromisoformat(payload[date_field].replace('Z', ''))
                else:
                    errors[date_field] = f'{date_field}는 ISO 날짜 형식(YYYY-MM-DD)이어야 합니다'
            except:
                errors[date_field] = f'{date_field}는 ISO 날짜 형식(YYYY-MM-DD)이어야 합니다'
    
    return errors

def create_contract_event(contract_id, event_type, meta=None, actor_id=None):
    """계약서 이벤트 생성"""
    event = ContractEvent(
        contract_id=contract_id,
        actor_id=actor_id,
        event_type=event_type,
        meta=meta or {}
    )
    db.session.add(event)
    return event

@bp.route('/contracts', methods=['POST'])
def create_contract():
    """계약서 생성"""
    try:
        # 요청 데이터 로깅 (개발 환경)
        print(f"=== CONTRACT CREATION REQUEST ===")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        
        # payload 정규화
        payload = request.get_json(silent=True) or {}
        print(f"Received payload: {str(payload)[:2000]}...")  # 최대 2KB 로깅
        
        # 개발용: user_id를 1로 고정
        user_id = 1
        
        # 새로운 validation 로직
        validation_errors = validate_contract_request(payload)
        if validation_errors:
            print(f"VALIDATION ERRORS: {validation_errors}")
            print(f"Payload that failed validation: {payload}")
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'details': validation_errors
            }), 400
        
        # 계약 유형
        contract_type = ContractType(payload['type'])
        
        # 금액 필드 설정 (validation 통과 후)
        sale_price = payload.get('sale_price')
        deposit = payload.get('deposit')
        monthly_rent = payload.get('monthly_rent')
        
        # 날짜 파싱
        contract_date = None
        handover_date = None
        
        if payload.get('contract_date'):
            try:
                from datetime import datetime
                contract_date = datetime.fromisoformat(payload['contract_date'].replace('Z', '')).date()
            except:
                return jsonify({'error': 'contract_date는 ISO 날짜 형식(YYYY-MM-DD)이어야 합니다'}), 400
        
        if payload.get('handover_date'):
            try:
                from datetime import datetime
                handover_date = datetime.fromisoformat(payload['handover_date'].replace('Z', '')).date()
            except:
                return jsonify({'error': 'handover_date는 ISO 날짜 형식(YYYY-MM-DD)이어야 합니다'}), 400
        
        # parties에서 SELLER/BUYER 정보 추출
        parties = payload.get('parties', [])
        seller_info = next((p for p in parties if p.get('role') == 'SELLER'), {})
        buyer_info = next((p for p in parties if p.get('role') == 'BUYER'), {})
        
        # 계약서 생성
        contract = Contract(
            user_id=user_id,
            type=contract_type,
            seller_name=seller_info.get('name', '').strip(),
            seller_phone=seller_info.get('phone', '').strip(),
            buyer_name=buyer_info.get('name', '').strip(),
            buyer_phone=buyer_info.get('phone', '').strip(),
            property_address=payload.get('property_address_full', '').strip(),
            # 타입별 금액 필드
            sale_price=sale_price,
            deposit=deposit,
            monthly_rent=monthly_rent,
            # 날짜 필드
            contract_date=contract_date,
            handover_date=handover_date,
            mgmt_note=payload.get('mgmt_note'),
            schedule=payload.get('schedule'),
            brokerage=payload.get('brokerage'),
            attachments=payload.get('attachments'),
            special_terms=payload.get('special_terms')
        )
        
        # 문서 해시 계산
        contract.doc_hash = contract.calculate_hash()
        
        db.session.add(contract)
        db.session.flush()  # ID 생성
        
        # 서명 placeholder 생성 (계약 유형에 따라)
        from models import ContractSignature, SignatureRole
        
        # 계약 유형에 따른 서명 역할 결정
        if contract_type == ContractType.SALE:
            signature_roles = [SignatureRole.SELLER, SignatureRole.BUYER, SignatureRole.AGENT]
        else:  # JEONSE, WOLSE
            signature_roles = [SignatureRole.LESSOR, SignatureRole.LESSEE, SignatureRole.BROKER]
        
        for role in signature_roles:
            signature = ContractSignature(
                contract_id=contract.id,
                role=role,
                signed_at=None  # 아직 서명하지 않음
            )
            db.session.add(signature)
        
        # 서명 데이터가 있으면 처리
        signatures_data = payload.get('signatures', {})
        if signatures_data:
            import base64
            import os
            
            for role_name, signature_data in signatures_data.items():
                if signature_data and len(signature_data) > 20:  # 유효한 서명 데이터인지 확인
                    try:
                        # 역할 매핑 (계약 유형에 따라)
                        if contract_type == ContractType.SALE:
                            role_mapping = {
                                'seller': SignatureRole.SELLER,
                                'buyer': SignatureRole.BUYER,
                                'broker': SignatureRole.AGENT
                            }
                        else:  # JEONSE, WOLSE
                            role_mapping = {
                                'lessor': SignatureRole.LESSOR,
                                'lessee': SignatureRole.LESSEE,
                                'broker': SignatureRole.BROKER
                            }
                        
                        signature_role = role_mapping.get(role_name.lower())
                        if signature_role:
                            # 서명 레코드 찾기
                            signature_record = ContractSignature.query.filter_by(
                                contract_id=contract.id,
                                role=signature_role
                            ).first()
                            
                            if signature_record:
                                # base64 데이터 처리
                                if signature_data.startswith('data:image'):
                                    signature_data = signature_data.split(',')[1]
                                
                                # base64 디코딩
                                image_bytes = base64.b64decode(signature_data)
                                
                                # 파일 저장
                                upload_dir = f"uploads/signatures/{contract.id}"
                                os.makedirs(upload_dir, exist_ok=True)
                                
                                filename = f"{role_name.lower()}.png"
                                file_path = os.path.join(upload_dir, filename)
                                
                                with open(file_path, 'wb') as f:
                                    f.write(image_bytes)
                                
                                # 서명 정보 업데이트
                                signature_record.image_path = file_path
                                signature_record.signed_at = datetime.utcnow()
                                signature_record.ip = request.remote_addr
                                signature_record.ua = request.headers.get('User-Agent')
                                
                    except Exception as e:
                        print(f"Signature processing error for {role_name}: {e}")
                        # 서명 처리 실패해도 계약서 생성은 계속 진행
        
        # 이벤트 생성
        create_contract_event(contract.id, 'CREATED', {
            'contract_type': contract_type.value,
            'seller_name': contract.seller_name,
            'buyer_name': contract.buyer_name
        })
        
        db.session.commit()
        
        return jsonify({'id': contract.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Contract creation error: {e}")
        return jsonify({'error': f'계약서 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@bp.route('/contracts', methods=['GET'])
def list_contracts():
    """계약서 목록 조회"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        q = request.args.get('q', '').strip()
        contract_type = request.args.get('type')
        
        # 기본 쿼리 - SQLAlchemy 인스턴스 충돌 방지
        try:
            query = Contract.query
        except Exception as e:
            print(f"Query error: {e}")
            # 대안: 직접 세션 사용
            from flask import current_app
            query = current_app.db.session.query(Contract)
        
        # 검색 필터
        if q:
            search_filter = f"%{q}%"
            query = query.filter(
                or_(
                    Contract.seller_name.ilike(search_filter),
                    Contract.buyer_name.ilike(search_filter),
                    Contract.property_address.ilike(search_filter),
                    Contract.doc_no.ilike(search_filter)
                )
            )
        
        # 유형 필터
        if contract_type:
            try:
                # ContractType enum 값 확인
                valid_types = [t.value for t in ContractType]
                if contract_type.upper() in valid_types:
                    query = query.filter(Contract.type == ContractType(contract_type.upper()))
                else:
                    return jsonify({'error': '유효하지 않은 계약 유형입니다'}), 400
            except (ValueError, AttributeError) as e:
                print(f"Contract type filter error: {e}")
                return jsonify({'error': '유효하지 않은 계약 유형입니다'}), 400
        
        # 페이지네이션
        pagination = query.order_by(Contract.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        contracts = [contract.to_dict() for contract in pagination.items]
        
        return jsonify({
            'contracts': contracts,
            'page': page,
            'pages': pagination.pages,
            'total': pagination.total
        }), 200
        
    except Exception as e:
        print(f"List contracts error: {e}")
        import traceback
        traceback.print_exc()
        
        # 더 자세한 에러 정보
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'request_args': dict(request.args),
            'traceback': traceback.format_exc()
        }
        print(f"Detailed error: {error_details}")
        
        return jsonify({
            'error': f'계약서 목록 조회 중 오류가 발생했습니다: {str(e)}',
            'details': error_details
        }), 500

@bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """계약서 단건 조회"""
    try:
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        return jsonify({'contract': contract.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': '계약서 조회 중 오류가 발생했습니다'}), 500

@bp.route('/contracts/<int:contract_id>/pdf', methods=['GET'])
def get_contract_pdf(contract_id):
    """계약서 PDF 생성 및 다운로드"""
    try:
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        
        # PDF 생성 - WeasyPrint 기반 PDF 렌더러 사용
        from pdf.pdf_renderer import render_contract_pdf
        pdf_content = render_contract_pdf(contract)
        
        # 이벤트 생성
        create_contract_event(contract.id, 'PDF_GENERATED', {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        db.session.commit()
        
        # 모드에 따른 응답 설정
        mode = request.args.get('mode', 'inline')
        filename = f"contract_{contract.id}_{contract.type.value.lower()}.pdf"
        
        if mode == 'download':
            # 다운로드용 응답
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
                as_attachment=False,
                download_name=filename
            )
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({'error': f'PDF 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@bp.route('/contracts/<int:contract_id>/signatures/<int:signature_id>.png', methods=['GET'])
def get_signature_image(contract_id, signature_id):
    """서명 이미지 조회"""
    try:
        from models import ContractSignature
        import os
        
        # 계약서와 서명 존재 확인
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        signature = ContractSignature.query.filter_by(
            id=signature_id, 
            contract_id=contract_id
        ).first_or_404()
        
        # 실제 서명 이미지 파일이 있는지 확인
        if signature.image_path and os.path.exists(signature.image_path):
            return send_file(
                signature.image_path,
                mimetype='image/png',
                as_attachment=False
            )
        else:
            # 서명이 없는 경우 404 반환 (정상적인 동작)
            return jsonify({'error': '서명 이미지를 찾을 수 없습니다'}), 404
        
    except Exception as e:
        print(f"Signature image error: {e}")
        return jsonify({'error': '서명 이미지를 불러올 수 없습니다'}), 404

@bp.route('/contracts/<int:contract_id>/pdf/preview', methods=['GET'])
def get_contract_pdf_preview(contract_id):
    """계약서 PDF 미리보기 (서명 포함)"""
    try:
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        include = request.args.get('include', '')
        include_signatures = 'signatures' in include
        include_stamps = 'stamps' in include
        
        # PDF 생성 (서명/도장 포함 옵션)
        pdf_generator = StandardContractPDF()
        pdf_buffer = pdf_generator.generate_contract_pdf(
            contract, 
            include_signatures=include_signatures,
            include_stamps=include_stamps
        )
        
        # 이벤트 생성
        create_contract_event(contract.id, 'PDF_PREVIEW_GENERATED', {
            'include_signatures': include_signatures,
            'include_stamps': include_stamps,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        db.session.commit()
        
        # PDF 응답
        pdf_buffer.seek(0)
        filename = f"contract_{contract.id}_preview.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=filename
        )
        
    except Exception as e:
        print(f"PDF preview generation error: {e}")
        return jsonify({'error': f'PDF 미리보기 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@bp.route('/contracts/<int:contract_id>/signatures/<string:role>', methods=['PUT'])
def upload_signature(contract_id, role):
    """서명 업로드"""
    try:
        from models import ContractSignature, SignatureRole
        import os
        from werkzeug.utils import secure_filename
        
        # 계약서 존재 확인
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        
        # 역할 검증
        try:
            signature_role = SignatureRole(role.upper())
        except ValueError:
            return jsonify({'error': '유효하지 않은 서명 역할입니다'}), 400
        
        # 서명 레코드 찾기
        signature = ContractSignature.query.filter_by(
            contract_id=contract_id,
            role=signature_role
        ).first()
        
        if not signature:
            return jsonify({'error': '서명 레코드를 찾을 수 없습니다'}), 404
        
        # 파일 업로드 처리
        if 'file' in request.files:
            # multipart/form-data로 파일 업로드
            file = request.files['file']
            if file and file.filename:
                # 파일 저장 경로 생성
                upload_dir = f"uploads/signatures/{contract_id}"
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = f"{role.lower()}.png"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                signature.image_path = file_path
                signature.signed_at = datetime.utcnow()
                signature.ip = request.remote_addr
                signature.ua = request.headers.get('User-Agent')
                
        elif 'image' in request.json:
            # JSON base64로 이미지 업로드
            import base64
            image_data = request.json['image']
            if image_data.startswith('data:image'):
                # data:image/png;base64, 부분 제거
                image_data = image_data.split(',')[1]
            
            # base64 디코딩
            image_bytes = base64.b64decode(image_data)
            
            # 파일 저장
            upload_dir = f"uploads/signatures/{contract_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = f"{role.lower()}.png"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            signature.image_path = file_path
            signature.signed_at = datetime.utcnow()
            signature.ip = request.remote_addr
            signature.ua = request.headers.get('User-Agent')
        
        else:
            return jsonify({'error': '서명 이미지가 제공되지 않았습니다'}), 400
        
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'signature': signature.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Signature upload error: {e}")
        return jsonify({'error': f'서명 업로드 중 오류가 발생했습니다: {str(e)}'}), 500

@bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id):
    """계약서 삭제"""
    try:
        # 계약서 존재 확인
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        
        # 관련 데이터 삭제 (순서 중요)
        from models import ContractEvent, ContractSignature
        
        # 1. 서명 파일들 삭제
        import os
        import shutil
        signature_dir = f"uploads/signatures/{contract_id}"
        if os.path.exists(signature_dir):
            shutil.rmtree(signature_dir)
            print(f"Deleted signature directory: {signature_dir}")
        
        # 2. 관련 이벤트 삭제
        ContractEvent.query.filter_by(contract_id=contract_id).delete()
        
        # 3. 관련 서명 삭제
        ContractSignature.query.filter_by(contract_id=contract_id).delete()
        
        # 4. 계약서 삭제
        db.session.delete(contract)
        db.session.commit()
        
        return jsonify({
            'message': '계약서가 성공적으로 삭제되었습니다',
            'deleted_id': contract_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Contract deletion error: {e}")
        return jsonify({'error': f'계약서 삭제 중 오류가 발생했습니다: {str(e)}'}), 500

# 전자서명 목업 (선택사항)
@bp.route('/contracts/<int:contract_id>/sign-requests', methods=['POST'])
def create_sign_request(contract_id):
    """서명 요청 생성 (목업)"""
    try:
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        data = request.get_json()
        
        role = data.get('role')  # SELLER, BUYER, AGENT
        
        # 목업 응답
        return jsonify({
            'sign_request_id': f"SR_{contract_id}_{role}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'status': 'PENDING',
            'message': '서명 요청이 생성되었습니다 (목업)'
        }), 201
        
    except Exception as e:
        return jsonify({'error': '서명 요청 생성 중 오류가 발생했습니다'}), 500

@bp.route('/contracts/<int:contract_id>/sign-callback', methods=['POST'])
def sign_callback(contract_id):
    """서명 콜백 처리 (목업)"""
    try:
        try:
            contract = Contract.query.get_or_404(contract_id)
        except Exception as e:
            from flask import current_app
            contract = current_app.db.session.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                from flask import abort
                abort(404)
        data = request.get_json()
        
        # 목업: 서명 완료 처리
        contract.status = ContractStatus.SIGNED
        
        # 이벤트 생성
        create_contract_event(contract.id, 'SIGNED', {
            'role': data.get('role'),
            'auth_method': data.get('auth_method'),
            'ip': request.remote_addr
        })
        
        db.session.commit()
        
        return jsonify({
            'status': 'SIGNED',
            'message': '서명이 완료되었습니다 (목업)'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '서명 처리 중 오류가 발생했습니다'}), 500
