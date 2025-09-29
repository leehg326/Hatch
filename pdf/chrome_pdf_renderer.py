#!/usr/bin/env python3
"""
Chrome Headless를 사용한 PDF 렌더러
"""

import os
import subprocess
import tempfile
import time
from flask import current_app

class ChromePDFRenderer:
    """Chrome Headless PDF 렌더러"""
    
    def __init__(self):
        self.chrome_path = self._find_chrome()
    
    def _find_chrome(self):
        """Chrome 실행 파일 경로 찾기"""
        chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"Chrome 발견: {path}")
                return path
        
        print("Chrome을 찾을 수 없습니다.")
        return None
    
    def render_html_to_pdf(self, html_string, out_path=None, base_url=None):
        """
        HTML을 PDF로 변환
        """
        if not self.chrome_path:
            print("Chrome이 설치되지 않았습니다.")
            return None
        
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
            
            # Chrome 명령어 구성
            cmd = [
                self.chrome_path,
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
                '--virtual-time-budget=5000',
                'file://' + html_file
            ]
            
            print(f"Chrome PDF 생성 실행...")
            
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
                return None
                
        except Exception as e:
            print(f"Chrome PDF 생성 오류: {e}")
            return None
