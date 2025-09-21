#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import os
from flask_migrate import init, migrate, upgrade
from app import create_app
from models import db

def init_database():
    """데이터베이스 초기화"""
    app = create_app()
    
    with app.app_context():
        # 마이그레이션 폴더 초기화
        if not os.path.exists('migrations'):
            print("마이그레이션 폴더 초기화 중...")
            init()
        
        # 마이그레이션 파일 생성
        print("마이그레이션 파일 생성 중...")
        migrate(message='Initial migration')
        
        # 데이터베이스 업그레이드
        print("데이터베이스 업그레이드 중...")
        upgrade()
        
        print("✅ 데이터베이스 초기화 완료!")

if __name__ == '__main__':
    init_database()





