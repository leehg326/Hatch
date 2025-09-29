#!/usr/bin/env python3
"""
폰트 파일 존재 여부 확인 스크립트
"""

import os
from app import create_app

def check_fonts():
    app = create_app()
    with app.app_context():
        static_folder = app.static_folder
        font_folder = os.path.join(static_folder, 'fonts')
        
        print(f"폰트 폴더: {font_folder}")
        print(f"폰트 폴더 존재: {os.path.exists(font_folder)}")
        
        if os.path.exists(font_folder):
            files = os.listdir(font_folder)
            print(f"폰트 폴더 내 파일들: {files}")
        
        # 필요한 폰트 파일들
        required_fonts = [
            'NotoSansKR-Regular.ttf',
            'NotoSansKR-Medium.ttf', 
            'NotoSansKR-Bold.ttf'
        ]
        
        print("\n=== 폰트 파일 상태 ===")
        for font_name in required_fonts:
            font_path = os.path.join(font_folder, font_name)
            exists = os.path.exists(font_path)
            size = os.path.getsize(font_path) if exists else 0
            print(f"{font_name}: {'✓' if exists else '✗'} ({size} bytes)")
        
        print("\n=== 폰트 다운로드 안내 ===")
        print("1. https://fonts.google.com/noto/specimen/Noto+Sans+KR 방문")
        print("2. 'Download family' 클릭")
        print("3. 다운로드된 파일을 압축 해제")
        print("4. 다음 파일들을 static/fonts/ 폴더에 복사:")
        for font in required_fonts:
            print(f"   - {font}")

if __name__ == '__main__':
    check_fonts()
