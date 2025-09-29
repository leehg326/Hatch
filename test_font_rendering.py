#!/usr/bin/env python3
"""
한글 폰트 렌더링 테스트
"""

import os
from app import create_app
from flask import render_template
from pdf.pdf_renderer import PDFRenderer

def test_font_rendering():
    """한글 폰트 렌더링을 테스트합니다."""
    
    app = create_app()
    with app.app_context():
        # 계약서 데이터 (더미)
        contract_data = {
            'id': 28,
            'type': 'SALE',
            'doc_no': 'HATCH-2025-0001',
            'property_address': '서울특별시 강남구 테헤란로 123',
            'property_type': 'APARTMENT',
            'seller_name': '홍길동',
            'seller_phone': '010-1234-5678',
            'buyer_name': '김철수',
            'buyer_phone': '010-9876-5432',
            'broker_name': '이중개',
            'broker_phone': '010-5555-6666',
            'sale_price': 500000000,
            'deposit': 100000000,
            'balance': 400000000,
            'contract_date': '2025-09-29',
            'move_in_date': '2025-10-15',
            'special_terms': '특별한 조건 없음'
        }
        
        # HTML 템플릿 렌더링
        try:
            html_content = render_template('contracts/sale.html', contract=contract_data)
            print("HTML 템플릿 렌더링 성공!")
            
            # HTML 파일로 저장
            with open('test_contract.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("HTML 파일 저장: test_contract.html")
            
            # PDF 렌더링 테스트
            renderer = PDFRenderer()
            pdf_content = renderer.render_html_to_pdf(html_content)
            
            if pdf_content:
                with open('test_contract_font.pdf', 'wb') as f:
                    f.write(pdf_content)
                print("PDF 파일 저장: test_contract_font.pdf")
                print(f"PDF 크기: {len(pdf_content)} bytes")
            else:
                print("PDF 생성 실패")
                
        except Exception as e:
            print(f"렌더링 실패: {e}")

if __name__ == '__main__':
    test_font_rendering()
