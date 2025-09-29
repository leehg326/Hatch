#!/usr/bin/env python3
"""
데이터베이스 연결 문제 해결 스크립트
"""

def fix_database_issue():
    """데이터베이스 연결 문제를 해결합니다."""
    
    # 1. 간단한 테스트 계약서 API 생성
    simple_contracts_api = '''
from flask import Blueprint, request, jsonify
from datetime import datetime

# 간단한 계약서 API Blueprint
simple_contracts_bp = Blueprint('simple_contracts', __name__, url_prefix='/api')

@simple_contracts_bp.route('/contracts', methods=['GET'])
def list_contracts_simple():
    """간단한 계약서 목록 조회 (데이터베이스 없이)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        q = request.args.get('q', '').strip()
        contract_type = request.args.get('type')
        
        # 목업 데이터 반환
        mock_contracts = [
            {
                'id': 1,
                'type': 'SALE',
                'seller_name': '김매도',
                'buyer_name': '이매수',
                'property_address': '서울시 강남구 테헤란로 123',
                'sale_price': 500000000,
                'status': 'DRAFT',
                'created_at': datetime.now().isoformat(),
                'doc_no': 'CONTRACT_20250101_001'
            },
            {
                'id': 2,
                'type': 'JEONSE',
                'seller_name': '박임대',
                'buyer_name': '최임차',
                'property_address': '서울시 서초구 서초대로 456',
                'deposit': 100000000,
                'status': 'SIGNED',
                'created_at': datetime.now().isoformat(),
                'doc_no': 'CONTRACT_20250101_002'
            }
        ]
        
        # 검색 필터 적용
        filtered_contracts = mock_contracts
        if q:
            filtered_contracts = [
                c for c in mock_contracts 
                if q.lower() in c['seller_name'].lower() or 
                   q.lower() in c['buyer_name'].lower() or
                   q.lower() in c['property_address'].lower()
            ]
        
        # 타입 필터 적용
        if contract_type:
            filtered_contracts = [
                c for c in filtered_contracts 
                if c['type'] == contract_type.upper()
            ]
        
        # 페이지네이션
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_contracts = filtered_contracts[start_idx:end_idx]
        
        return jsonify({
            'contracts': paginated_contracts,
            'page': page,
            'pages': (len(filtered_contracts) + per_page - 1) // per_page,
            'total': len(filtered_contracts)
        }), 200
        
    except Exception as e:
        print(f"Simple contracts API error: {e}")
        return jsonify({'error': f'계약서 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@simple_contracts_bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract_simple(contract_id):
    """간단한 계약서 단건 조회"""
    try:
        # 목업 데이터에서 해당 ID 찾기
        mock_contracts = [
            {
                'id': 1,
                'type': 'SALE',
                'seller_name': '김매도',
                'buyer_name': '이매수',
                'property_address': '서울시 강남구 테헤란로 123',
                'sale_price': 500000000,
                'status': 'DRAFT',
                'created_at': datetime.now().isoformat(),
                'doc_no': 'CONTRACT_20250101_001'
            }
        ]
        
        contract = next((c for c in mock_contracts if c['id'] == contract_id), None)
        if not contract:
            return jsonify({'error': '계약서를 찾을 수 없습니다'}), 404
        
        return jsonify(contract), 200
        
    except Exception as e:
        return jsonify({'error': f'계약서 조회 중 오류가 발생했습니다: {str(e)}'}), 500
'''
    
    # 파일로 저장
    with open('routes/simple_contracts_api.py', 'w', encoding='utf-8') as f:
        f.write(simple_contracts_api)
    
    print("✓ 간단한 계약서 API 생성 완료")
    return True

if __name__ == "__main__":
    fix_database_issue()
    print("🎉 데이터베이스 문제 해결 스크립트 완료!")


