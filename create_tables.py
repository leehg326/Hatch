#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
"""

from app import create_app
from models import db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("데이터베이스 테이블 생성 중...")
        db.create_all()
        print("테이블 생성 완료!")
        
        # 테이블 목록 확인
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"생성된 테이블: {tables}")
