#!/usr/bin/env python3
"""
DB 테스트 스크립트
"""

from app import create_app
from models import db, User
from security import hash_password

def test_db():
    try:
        app = create_app()
        print('✅ Flask 앱 생성 성공!')
    except Exception as e:
        print(f'❌ Flask 앱 생성 실패: {e}')
        return
    print('DB URI:', app.config.get('SQLALCHEMY_DATABASE_URI'))
    print('모든 설정 키들:', [k for k in app.config.keys() if 'SQL' in k or 'SECRET' in k])
    
    # 설정을 직접 확인
    print('직접 설정 확인:')
    print('  SQLALCHEMY_DATABASE_URI:', app.config.get('SQLALCHEMY_DATABASE_URI'))
    print('  SECRET_KEY:', app.config.get('SECRET_KEY'))
    
    # 설정을 강제로 다시 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    print('강제 설정 후 DB URI:', app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    with app.app_context():
        db.create_all()
        print('✅ 데이터베이스 테이블 생성 완료!')
        
        # 테스트 사용자 생성
        existing_user = User.query.filter_by(email='test@test.com').first()
        if existing_user:
            print('기존 사용자 존재:', existing_user.email, existing_user.name)
        else:
            user = User(
                name='테스트 사용자',
                email='test@test.com',
                password_hash=hash_password('password123'),
                is_email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            print('새 사용자 생성:', user.email, user.name)
        
        # 모든 사용자 조회
        users = User.query.all()
        print('DB의 모든 사용자:', [(u.email, u.name) for u in users])

if __name__ == '__main__':
    test_db()
