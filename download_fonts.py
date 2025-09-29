#!/usr/bin/env python3
"""
Noto Sans KR 폰트 다운로드 및 설정
"""

import os
import requests
import zipfile
from app import create_app

def download_fonts():
    """Noto Sans KR 폰트를 다운로드하고 설정합니다."""
    
    # 앱 컨텍스트 생성
    app = create_app()
    with app.app_context():
        static_folder = app.static_folder
        font_folder = os.path.join(static_folder, 'fonts')
        
        # 폰트 폴더 생성
        os.makedirs(font_folder, exist_ok=True)
        
        print("Noto Sans KR 폰트 다운로드 중...")
        
        # Google Fonts에서 Noto Sans KR 다운로드
        font_url = "https://fonts.google.com/download?family=Noto%20Sans%20KR"
        
        try:
            # 폰트 다운로드
            response = requests.get(font_url, stream=True)
            response.raise_for_status()
            
            # 임시 zip 파일 저장
            zip_path = os.path.join(font_folder, 'noto-sans-kr.zip')
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"폰트 다운로드 완료: {zip_path}")
            
            # ZIP 파일 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(font_folder)
            
            print("폰트 압축 해제 완료")
            
            # 필요한 TTF 파일들 찾기
            ttf_files = []
            for root, dirs, files in os.walk(font_folder):
                for file in files:
                    if file.endswith('.ttf') and 'NotoSansKR' in file:
                        ttf_files.append(os.path.join(root, file))
            
            print(f"발견된 TTF 파일들: {ttf_files}")
            
            # Regular, Medium, Bold 파일 찾기
            target_files = {
                'NotoSansKR-Regular.ttf': None,
                'NotoSansKR-Medium.ttf': None,
                'NotoSansKR-Bold.ttf': None
            }
            
            for ttf_file in ttf_files:
                filename = os.path.basename(ttf_file)
                if 'Regular' in filename:
                    target_files['NotoSansKR-Regular.ttf'] = ttf_file
                elif 'Medium' in filename:
                    target_files['NotoSansKR-Medium.ttf'] = ttf_file
                elif 'Bold' in filename:
                    target_files['NotoSansKR-Bold.ttf'] = ttf_file
            
            # 파일 복사
            for target_name, source_path in target_files.items():
                if source_path and os.path.exists(source_path):
                    target_path = os.path.join(font_folder, target_name)
                    with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                        dst.write(src.read())
                    print(f"복사 완료: {target_name}")
                else:
                    print(f"파일을 찾을 수 없음: {target_name}")
            
            # 임시 파일 정리
            os.remove(zip_path)
            print("임시 파일 정리 완료")
            
        except Exception as e:
            print(f"폰트 다운로드 실패: {e}")
            print("수동으로 폰트를 다운로드하세요:")
            print("1. https://fonts.google.com/noto/specimen/Noto+Sans+KR 방문")
            print("2. 'Download family' 클릭")
            print("3. 다운로드된 ZIP 파일을 압축 해제")
            print("4. TTF 파일들을 app/static/fonts/ 폴더에 복사")

if __name__ == '__main__':
    download_fonts()
