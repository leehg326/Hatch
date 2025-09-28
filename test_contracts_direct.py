#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from routes.contracts import bp

app = create_app()

# Blueprint 등록 확인
print("Blueprint 등록 확인:")
for rule in app.url_map.iter_rules():
    if 'contracts' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint} ({rule.methods})")

# 직접 함수 테스트
print("\n직접 함수 테스트:")
with app.app_context():
    from routes.contracts import get_contracts
    print("get_contracts 함수 import 성공")
    
    # Flask request context 생성
    with app.test_request_context('/api/contracts/?per_page=5'):
        try:
            from flask import request
            print(f"Request URL: {request.url}")
            print(f"Request args: {dict(request.args)}")
            
            # 함수 직접 호출
            result = get_contracts()
            print(f"함수 결과: {result}")
        except Exception as e:
            print(f"함수 실행 오류: {e}")
            import traceback
            traceback.print_exc()

