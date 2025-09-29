#!/usr/bin/env python3
"""
간단한 한글 PDF 테스트
"""

from pdf.pdf_renderer import PDFRenderer

def test_simple_korean():
    """간단한 한글 텍스트로 PDF 테스트"""
    
    # 간단한 한글 HTML (인라인 스타일로 강제 설정)
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {
                font-family: 'Malgun Gothic';
                src: url('C:/Windows/Fonts/malgun.ttf') format('truetype');
            }
            @font-face {
                font-family: 'Gulim';
                src: url('C:/Windows/Fonts/gulim.ttc') format('truetype');
            }
            @font-face {
                font-family: 'Dotum';
                src: url('C:/Windows/Fonts/dotum.ttc') format('truetype');
            }
            
            * {
                font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', 'Dotum', sans-serif !important;
            }
            
            body {
                font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', 'Dotum', sans-serif !important;
                font-size: 14px;
                line-height: 1.6;
                margin: 20px;
            }
            h1 {
                font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', 'Dotum', sans-serif !important;
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }
            p {
                font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', 'Dotum', sans-serif !important;
                margin: 10px 0;
            }
            .test-text {
                font-family: 'Malgun Gothic', '맑은 고딕', 'Gulim', 'Dotum', sans-serif !important;
                font-size: 16px;
                font-weight: bold;
                color: #000;
            }
        </style>
    </head>
    <body>
        <h1>한글 폰트 테스트</h1>
        <p class="test-text">가나다라마바사 아자차카타파하</p>
        <p class="test-text">부동산 매매계약서</p>
        <p class="test-text">홍길동 김철수 이중개</p>
        <p class="test-text">서울특별시 강남구 테헤란로 123</p>
        <p class="test-text">매매가격: 5억원</p>
        <p class="test-text">계약일자: 2025년 9월 29일</p>
        <p class="test-text">특약사항: 특별한 조건 없음</p>
        <p class="test-text">한글 텍스트가 정상적으로 표시되는지 확인합니다.</p>
    </body>
    </html>
    """
    
    try:
        # PDF 렌더러 생성
        renderer = PDFRenderer()
        
        # PDF 생성
        pdf_content = renderer.render_html_to_pdf(html_content)
        
        if pdf_content:
            # PDF 파일 저장
            with open('simple_korean_test.pdf', 'wb') as f:
                f.write(pdf_content)
            
            print("간단한 한글 PDF 생성 성공!")
            print(f"PDF 크기: {len(pdf_content)} bytes")
            print("파일 저장: simple_korean_test.pdf")
            
            # 한글 텍스트 확인
            korean_texts = [
                '가나다라마바사',
                '부동산 매매계약서',
                '홍길동',
                '서울특별시',
                '매매가격'
            ]
            
            for text in korean_texts:
                if text.encode('utf-8') in pdf_content:
                    print(f"✓ '{text}' 텍스트가 PDF에 포함됨")
                else:
                    print(f"✗ '{text}' 텍스트가 PDF에 없음")
        else:
            print("PDF 생성 실패")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == '__main__':
    test_simple_korean()
