#!/usr/bin/env python3
"""
대안 PDF 렌더러 - 한글 폰트 문제 해결
"""

import os
import subprocess
import tempfile
from flask import current_app

class AlternativePDFRenderer:
    """대안 PDF 렌더러"""
    
    def __init__(self):
        self.base_url = None
    
    def render_html_to_pdf(self, html_string, out_path=None, base_url=None):
        """
        HTML을 PDF로 변환 (대안 방법)
        """
        try:
            # 임시 HTML 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_string)
                html_file = f.name
            
            # 임시 PDF 파일 경로
            if out_path:
                pdf_file = out_path
            else:
                pdf_file = tempfile.mktemp(suffix='.pdf')
            
            # Chrome/Chromium을 사용한 PDF 생성
            chrome_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if not chrome_path:
                print("Chrome을 찾을 수 없습니다. WeasyPrint로 폴백합니다.")
                return self._fallback_weasyprint(html_string, out_path)
            
            # Chrome 명령어 구성
            cmd = [
                chrome_path,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--print-to-pdf=' + pdf_file,
                '--print-to-pdf-no-header',
                '--run-all-compositor-stages-before-draw',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                'file://' + html_file
            ]
            
            print(f"Chrome PDF 생성 실행: {' '.join(cmd)}")
            
            # Chrome 실행
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(pdf_file):
                print("Chrome PDF 생성 성공!")
                
                if out_path:
                    return None
                else:
                    # PDF 파일 읽기
                    with open(pdf_file, 'rb') as f:
                        pdf_content = f.read()
                    
                    # 임시 파일 정리
                    os.unlink(html_file)
                    os.unlink(pdf_file)
                    
                    return pdf_content
            else:
                print(f"Chrome PDF 생성 실패: {result.stderr}")
                return self._fallback_weasyprint(html_string, out_path)
                
        except Exception as e:
            print(f"대안 PDF 생성 실패: {e}")
            return self._fallback_weasyprint(html_string, out_path)
    
    def _fallback_weasyprint(self, html_string, out_path):
        """WeasyPrint 폴백"""
        try:
            from pdf.pdf_renderer import PDFRenderer
            renderer = PDFRenderer()
            return renderer.render_html_to_pdf(html_string, out_path)
        except Exception as e:
            print(f"WeasyPrint 폴백도 실패: {e}")
            return None
