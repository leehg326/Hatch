#!/usr/bin/env python3
"""
PDF 서명 합성 유틸리티
"""

import os
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from models import Contract, ContractSignature, db
from flask import current_app

class SignatureIntegrator:
    """서명 통합 클래스"""
    
    def __init__(self):
        self.signature_positions = {
            'SELLER': {'x': 50, 'y': 200, 'width': 120, 'height': 60},
            'BUYER': {'x': 200, 'y': 200, 'width': 120, 'height': 60},
            'AGENT': {'x': 350, 'y': 200, 'width': 120, 'height': 60},
            'LESSOR': {'x': 50, 'y': 200, 'width': 120, 'height': 60},
            'LESSEE': {'x': 200, 'y': 200, 'width': 120, 'height': 60},
            'BROKER': {'x': 350, 'y': 200, 'width': 120, 'height': 60}
        }
    
    def get_signature_image(self, signature_path):
        """서명 이미지 로드 및 전처리"""
        if not signature_path or not os.path.exists(signature_path):
            return None
        
        try:
            # PIL로 이미지 로드
            img = Image.open(signature_path)
            
            # RGBA 모드로 변환 (투명도 지원)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 크기 조정 (서명 필드에 맞게)
            img.thumbnail((120, 60), Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            current_app.logger.error(f"서명 이미지 로드 실패: {e}")
            return None
    
    def create_signature_overlay(self, signatures):
        """서명 오버레이 이미지 생성"""
        # A4 크기 기준 (210mm x 297mm, 300 DPI)
        width, height = 2480, 3508  # A4 at 300 DPI
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        for signature in signatures:
            if not signature.image_path:
                continue
            
            role = signature.role.value
            if role not in self.signature_positions:
                continue
            
            pos = self.signature_positions[role]
            sig_img = self.get_signature_image(signature.image_path)
            
            if sig_img:
                # 서명 이미지를 오버레이에 합성
                x = int(pos['x'] * 3.78)  # mm to pixels (300 DPI)
                y = int(pos['y'] * 3.78)
                
                # 투명도 유지하면서 합성
                overlay.paste(sig_img, (x, y), sig_img)
        
        return overlay
    
    def integrate_signatures_to_pdf(self, contract, html_content, css_path):
        """서명을 PDF에 통합"""
        try:
            # 서명 정보 로드
            signatures = ContractSignature.query.filter_by(contract_id=contract.id).all()
            
            if not signatures:
                # 서명이 없으면 일반 PDF 생성
                return self.generate_pdf_without_signatures(html_content, css_path)
            
            # 서명 오버레이 생성
            signature_overlay = self.create_signature_overlay(signatures)
            
            # HTML에 서명 정보 주입
            enhanced_html = self.inject_signature_data(html_content, signatures)
            
            # PDF 생성
            font_config = FontConfiguration()
            html_doc = HTML(string=enhanced_html, base_url='')
            css_doc = CSS(filename=css_path, font_config=font_config)
            
            pdf_content = html_doc.write_pdf(stylesheets=[css_doc], font_config=font_config)
            
            return pdf_content
            
        except Exception as e:
            current_app.logger.error(f"서명 통합 실패: {e}")
            # 서명 통합 실패 시 일반 PDF 반환
            return self.generate_pdf_without_signatures(html_content, css_path)
    
    def generate_pdf_without_signatures(self, html_content, css_path):
        """서명 없는 PDF 생성"""
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content, base_url='')
        css_doc = CSS(filename=css_path, font_config=font_config)
        
        return html_doc.write_pdf(stylesheets=[css_doc], font_config=font_config)
    
    def inject_signature_data(self, html_content, signatures):
        """HTML에 서명 데이터 주입"""
        # 서명 정보를 JSON으로 변환
        signature_data = []
        for sig in signatures:
            signature_data.append({
                'role': sig.role.value,
                'image_path': sig.image_path,
                'signed_at': sig.signed_at.isoformat() if sig.signed_at else None,
                'auth_method': sig.auth_method.value if sig.auth_method else None
            })
        
        # HTML에 서명 데이터 주입
        signature_json = str(signature_data).replace("'", '"')
        
        # HTML에 서명 데이터 스크립트 추가
        script_tag = f"""
        <script type="application/json" id="signature-data">
        {signature_json}
        </script>
        """
        
        # </head> 태그 앞에 스크립트 삽입
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{script_tag}</head>')
        else:
            html_content = f'{script_tag}{html_content}'
        
        return html_content
    
    def create_signature_watermark(self, contract):
        """서명 워터마크 생성"""
        watermark_text = f"서명완료 - {contract.doc_no}"
        
        # 워터마크 이미지 생성
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            # 폰트 로드 (시스템 기본 폰트 사용)
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # 워터마크 텍스트 그리기
        draw.text((10, 40), watermark_text, fill=(0, 0, 0, 128), font=font)
        
        return img
    
    def verify_signature_integrity(self, contract):
        """서명 무결성 검증"""
        try:
            signatures = ContractSignature.query.filter_by(contract_id=contract.id).all()
            
            verification_results = []
            for sig in signatures:
                result = {
                    'role': sig.role.value,
                    'has_image': bool(sig.image_path and os.path.exists(sig.image_path)),
                    'signed_at': sig.signed_at.isoformat() if sig.signed_at else None,
                    'auth_method': sig.auth_method.value if sig.auth_method else None,
                    'is_valid': bool(sig.signed_payload_hash)
                }
                verification_results.append(result)
            
            return {
                'contract_id': contract.id,
                'total_signatures': len(signatures),
                'verified_signatures': len([r for r in verification_results if r['is_valid']]),
                'signatures': verification_results
            }
            
        except Exception as e:
            current_app.logger.error(f"서명 무결성 검증 실패: {e}")
            return None

# 전역 서명 통합자 인스턴스
signature_integrator = SignatureIntegrator()

def integrate_contract_signatures(contract, html_content, css_path):
    """계약서 서명 통합 (외부 호출용)"""
    return signature_integrator.integrate_signatures_to_pdf(contract, html_content, css_path)

def verify_contract_signatures(contract):
    """계약서 서명 검증 (외부 호출용)"""
    return signature_integrator.verify_signature_integrity(contract)

