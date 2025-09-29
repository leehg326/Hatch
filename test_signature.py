#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_signature():
    """테스트용 서명 이미지 생성"""
    # 300x150 크기의 흰색 배경 이미지 생성
    img = Image.new('RGB', (300, 150), 'white')
    draw = ImageDraw.Draw(img)
    
    # 서명 텍스트 그리기
    try:
        # 한글 폰트 시도
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = "테스트 서명"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = (150 - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    # 업로드 디렉토리 생성
    upload_dir = "uploads/signatures/17"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 파일 저장
    file_path = os.path.join(upload_dir, "seller.png")
    img.save(file_path)
    
    print(f"Test signature created: {file_path}")
    return file_path

if __name__ == "__main__":
    create_test_signature()




