#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Flask 앱 초기화
from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    with app.app_context():
        try:
            # 기존 테이블이 있는지 확인
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"Existing tables: {existing_tables}")
            
            # 새로운 컬럼 추가 (ALTER TABLE)
            if 'contracts' in existing_tables:
                print("Adding new columns to contracts table...")
                
                # sale_price 컬럼 추가
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text("ALTER TABLE contracts ADD COLUMN sale_price INTEGER"))
                    print("✓ Added sale_price column")
                except Exception as e:
                    print(f"  sale_price column may already exist: {e}")
                
                # contract_date 컬럼 추가
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text("ALTER TABLE contracts ADD COLUMN contract_date DATE"))
                    print("✓ Added contract_date column")
                except Exception as e:
                    print(f"  contract_date column may already exist: {e}")
                
                # handover_date 컬럼 추가
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text("ALTER TABLE contracts ADD COLUMN handover_date DATE"))
                    print("✓ Added handover_date column")
                except Exception as e:
                    print(f"  handover_date column may already exist: {e}")
            
            if 'contract_signatures' in existing_tables:
                print("Adding new columns to contract_signatures table...")
                
                # image_path 컬럼 추가
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text("ALTER TABLE contract_signatures ADD COLUMN image_path TEXT"))
                    print("✓ Added image_path column")
                except Exception as e:
                    print(f"  image_path column may already exist: {e}")
            
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            return False
        
        return True

if __name__ == "__main__":
    migrate_database()
