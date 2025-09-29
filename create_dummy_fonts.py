#!/usr/bin/env python3
"""
더미 폰트 파일 생성 (테스트용)
실제 운영에서는 Google Fonts에서 다운로드한 TTF 파일을 사용해야 합니다.
"""

import os
from app import create_app

def create_dummy_fonts():
    app = create_app()
    with app.app_context():
        static_folder = app.static_folder
        font_folder = os.path.join(static_folder, 'fonts')
        
        # 폰트 폴더 생성
        os.makedirs(font_folder, exist_ok=True)
        
        # 더미 폰트 파일들 생성 (실제 TTF가 아닌 텍스트 파일)
        dummy_fonts = [
            'NotoSansKR-Regular.ttf',
            'NotoSansKR-Medium.ttf',
            'NotoSansKR-Bold.ttf'
        ]
        
        for font_name in dummy_fonts:
            font_path = os.path.join(font_folder, font_name)
            with open(font_path, 'w', encoding='utf-8') as f:
                f.write(f"# Dummy font file: {font_name}\n")
                f.write("# This is NOT a real TTF font file!\n")
                f.write("# Download actual fonts from: https://fonts.google.com/noto/specimen/Noto+Sans+KR\n")
                f.write("# Replace this file with the actual TTF font file.\n")
        
        print("더미 폰트 파일들이 생성되었습니다.")
        print("실제 운영에서는 Google Fonts에서 다운로드한 TTF 파일로 교체해야 합니다.")
        print("다운로드 링크: https://fonts.google.com/noto/specimen/Noto+Sans+KR")

if __name__ == '__main__':
    create_dummy_fonts()
