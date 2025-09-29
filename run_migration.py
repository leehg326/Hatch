#!/usr/bin/env python3
"""
마이그레이션 실행 스크립트
"""

from app import create_app
from flask_migrate import upgrade

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("마이그레이션 실행 중...")
        upgrade()
        print("마이그레이션 완료!")
