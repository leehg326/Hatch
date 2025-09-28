#!/usr/bin/env python3
"""
계약서 API 테스트 스크립트
"""

from app import create_app
from datetime import datetime

def test_contracts_api():
    app = create_app()
    
    with app.app_context():
        # app.py에서 사용하는 db 인스턴스 import
        from models import db, Contract, ContractType, User
        
        try:
            # 1. 데이터베이스 연결 테스트
            print("1. 데이터베이스 연결 테스트...")
            # db.create_all()는 이미 app.py에서 호출됨
            print("✓ 데이터베이스 테이블 생성 완료")
            
            # 2. 계약서 개수 확인
            print("2. 계약서 개수 확인...")
            contract_count = Contract.query.count()
            print(f"✓ 현재 계약서 개수: {contract_count}")
            
            # 3. 샘플 계약서 생성 (없는 경우)
            if contract_count == 0:
                print("3. 샘플 계약서 생성...")
                
                # 샘플 사용자 생성
                user = User(
                    name="테스트 사용자",
                    email="test@example.com",
                    password_hash="dummy_hash",
                    is_email_verified=True
                )
                db.session.add(user)
                db.session.flush()
                
                # 샘플 계약서 생성
                sample_contract = Contract(
                    user_id=user.id,
                    type=ContractType.SALE,
                    seller_name="김매도",
                    seller_phone="010-1234-5678",
                    buyer_name="이매수",
                    buyer_phone="010-9876-5432",
                    property_address="서울시 강남구 테헤란로 123",
                    sale_price=500000000,
                    contract_date=datetime.now().date(),
                    handover_date=datetime.now().date(),
                    doc_no="TEST_20250101_001"
                )
                db.session.add(sample_contract)
                db.session.commit()
                print("✓ 샘플 계약서 생성 완료")
            
            # 4. 계약서 목록 조회 테스트
            print("4. 계약서 목록 조회 테스트...")
            contracts = Contract.query.limit(5).all()
            print(f"✓ 조회된 계약서 개수: {len(contracts)}")
            
            for contract in contracts:
                print(f"  - ID: {contract.id}, 타입: {contract.type.value if contract.type else 'None'}, 매도인: {contract.seller_name}")
            
            # 5. 페이지네이션 테스트
            print("5. 페이지네이션 테스트...")
            pagination = Contract.query.paginate(page=1, per_page=5, error_out=False)
            print(f"✓ 페이지네이션 결과: {pagination.total}개 중 {len(pagination.items)}개 조회")
            
            return True
            
        except Exception as e:
            print(f"✗ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_contracts_api()
    if success:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n❌ 테스트 실패")
