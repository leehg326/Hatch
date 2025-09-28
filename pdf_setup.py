#!/usr/bin/env python3
"""
PDF 모듈 설정 및 Blueprint 등록 가이드
"""

# app.py 또는 메인 Flask 앱 파일에 다음 코드를 추가하세요:

"""
from routes.pdf_bp import pdf_bp

# Blueprint 등록
app.register_blueprint(pdf_bp)

# 또는 특정 URL prefix와 함께:
# app.register_blueprint(pdf_bp, url_prefix='/api/pdf')
"""

# 환경 변수 설정 (config.py 또는 .env 파일에 추가):
"""
PDF_SECURITY_SALT = 'your_secure_salt_here'
"""

# 데이터베이스 마이그레이션 (새로운 pdf_sha256 필드 추가):
"""
# migrations/versions/add_pdf_sha256.py 파일 생성 필요
"""

# 폰트 파일 설정:
"""
# static/fonts/ 디렉토리에 다음 폰트 파일들을 추가:
# - NotoSansKR-Regular.ttf
# - NotoSansKR-Bold.ttf
"""

# 사용 예시:
"""
# PDF 생성 및 다운로드
GET /api/contracts/{id}/pdf?mode=download

# PDF 미리보기
GET /api/contracts/{id}/pdf?mode=inline

# PDF 정보 조회
GET /api/contracts/{id}/pdf/info

# PDF 무결성 검증
POST /api/contracts/{id}/pdf/verify

# 보안 정보 조회
GET /api/contracts/{id}/security

# 서명 검증
POST /api/contracts/{id}/signatures/verify
"""

