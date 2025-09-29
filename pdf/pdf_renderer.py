#!/usr/bin/env python3
"""
PDF 렌더러 모듈 - WeasyPrint 기반 HTML→PDF 변환
한글 폰트 문제 완전 해결을 위한 통합 PDF 생성기
"""

import os
import io
from datetime import datetime
from flask import current_app
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from weasyprint import default_url_fetcher


class PDFRenderer:
    """WeasyPrint 기반 PDF 렌더러"""
    
    def __init__(self):
        self.base_url = None
        self.font_config = None
        self.setup_font_config()
    
    def setup_font_config(self):
        """폰트 설정 초기화"""
        try:
            # FontConfiguration으로 한글 폰트 지원
            self.font_config = FontConfiguration()
            print("폰트 설정 초기화 완료")
            
            # 시스템 폰트 확인
            system_fonts = [
                'C:/Windows/Fonts/malgun.ttf',
                'C:/Windows/Fonts/gulim.ttc',
                'C:/Windows/Fonts/dotum.ttc'
            ]
            
            available_fonts = []
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    available_fonts.append(font_path)
                    print(f"시스템 폰트 확인됨: {font_path}")
            
            print(f"사용 가능한 시스템 폰트: {len(available_fonts)}개")
                        
        except Exception as e:
            print(f"폰트 설정 실패: {e}")
            self.font_config = FontConfiguration()
    
    def render_html_to_pdf(self, html_string, out_path=None, base_url=None):
        """
        HTML 문자열을 PDF로 변환
        
        Args:
            html_string (str): HTML 내용
            out_path (str, optional): 출력 파일 경로. None이면 bytes 반환
            base_url (str, optional): 기본 URL. None이면 현재 앱의 static 폴더 사용
            
        Returns:
            bytes or None: PDF 바이트 데이터 (out_path가 None인 경우) 또는 None (파일 저장 시)
        """
        try:
            # base_url 설정 - 절대 URL 사용
            if base_url is None and current_app:
                from flask import url_for
                base_url = current_app.config.get('APP_BASE_URL', 'http://127.0.0.1:5000')
            elif base_url is None:
                base_url = 'http://127.0.0.1:5000'
            
            # HTML에서 상대 경로를 절대 URL로 변환
            if current_app:
                from flask import url_for
                # CSS 링크를 절대 URL로 변환
                html_string = html_string.replace(
                    'href="/static/', 
                    f'href="{url_for("static", filename="", _external=True)}'
                ).replace(
                    'src="/static/', 
                    f'src="{url_for("static", filename="", _external=True)}'
                )
            
            # CSS 파일 경로 (절대 URL)
            css_url = None
            if current_app:
                from flask import url_for
                css_url = url_for('static', filename='css/print.css', _external=True)
            else:
                css_url = f"{base_url}/static/css/print.css"
            
            # HTML 문서 생성
            html_doc = HTML(string=html_string, base_url=base_url)
            
            # CSS 문서 생성 (절대 URL 사용)
            css_doc = None
            if css_url:
                try:
                    css_doc = CSS(url=css_url, font_config=self.font_config)
                except Exception as css_error:
                    print(f"CSS 로드 실패: {css_error}")
                    # 로컬 파일로 폴백
                    css_path = os.path.join(current_app.static_folder, 'css', 'print.css') if current_app else None
                    if css_path and os.path.exists(css_path):
                        css_doc = CSS(filename=css_path, font_config=self.font_config)
            
            # PDF 생성 (한글 폰트 강제 적용)
            pdf_options = {
                'font_config': self.font_config,
                'optimize_images': False,  # 이미지 최적화 비활성화
                'jpeg_quality': 95,  # JPEG 품질 높임
            }
            
            if out_path:
                # 파일로 저장
                if css_doc:
                    html_doc.write_pdf(out_path, stylesheets=[css_doc], **pdf_options)
                else:
                    html_doc.write_pdf(out_path, **pdf_options)
                return None
            else:
                # 바이트 데이터로 반환
                if css_doc:
                    pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], **pdf_options)
                else:
                    pdf_bytes = html_doc.write_pdf(**pdf_options)
                return pdf_bytes
                
        except Exception as e:
            print(f"PDF 렌더링 실패: {e}")
            raise e
    
    def render_template_to_pdf(self, template_name, template_vars=None, out_path=None):
        """
        템플릿을 PDF로 렌더링
        
        Args:
            template_name (str): 템플릿 파일명
            template_vars (dict, optional): 템플릿 변수
            out_path (str, optional): 출력 파일 경로
            
        Returns:
            bytes or None: PDF 바이트 데이터
        """
        try:
            from flask import render_template
            
            if template_vars is None:
                template_vars = {}
            
            # 템플릿 렌더링
            html_content = render_template(template_name, **template_vars)
            
            # PDF 변환
            return self.render_html_to_pdf(html_content, out_path)
            
        except Exception as e:
            print(f"템플릿 PDF 렌더링 실패: {e}")
            raise e
    
    def render_contract_pdf(self, contract, template_name=None, out_path=None):
        """
        계약서 PDF 렌더링
        
        Args:
            contract: 계약 객체
            template_name (str, optional): 템플릿 파일명
            out_path (str, optional): 출력 파일 경로
            
        Returns:
            bytes or None: PDF 바이트 데이터
        """
        try:
            # 계약 유형에 따른 템플릿 선택
            if template_name is None:
                template_map = {
                    'SALE': 'contracts/sale.html',
                    'JEONSE': 'contracts/jeonse.html',
                    'WOLSE': 'contracts/wolse.html'
                }
                template_name = template_map.get(contract.type.value, 'contracts/sale.html')
            
            # 템플릿 변수 준비
            template_vars = {
                'contract': contract,
                'current_time': datetime.now(),
                'qr_code_data': self._generate_qr_code(contract),
                'watermark_data': self._generate_watermark(contract)
            }
            
            # 서명 정보 추가
            try:
                from models import ContractSignature
                signatures = ContractSignature.query.filter_by(contract_id=contract.id).all()
                template_vars['signatures'] = signatures
            except Exception as e:
                print(f"서명 정보 로드 실패: {e}")
                template_vars['signatures'] = []
            
            return self.render_template_to_pdf(template_name, template_vars, out_path)
            
        except Exception as e:
            print(f"계약서 PDF 렌더링 실패: {e}")
            raise e
    
    def _generate_qr_code(self, contract):
        """QR 코드 생성"""
        try:
            import qrcode
            import base64
            
            qr_data = f"CONTRACT_ID:{contract.id}|HASH:{contract.doc_hash[:16] if contract.doc_hash else 'N/A'}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=1,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # PIL Image를 base64로 변환
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return base64.b64encode(img_buffer.getvalue()).decode()
        except Exception as e:
            print(f"QR 코드 생성 실패: {e}")
            return None
    
    def _generate_watermark(self, contract):
        """워터마크 생성"""
        try:
            return {
                'contract_id': contract.id,
                'doc_no': contract.doc_no,
                'created_at': contract.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'hash': contract.doc_hash[:16] if contract.doc_hash else 'N/A'
            }
        except Exception as e:
            print(f"워터마크 생성 실패: {e}")
            return None


# 전역 인스턴스
pdf_renderer = PDFRenderer()


def render_html_to_pdf(html_string, out_path=None, base_url=None):
    """편의 함수: HTML을 PDF로 변환"""
    return pdf_renderer.render_html_to_pdf(html_string, out_path, base_url)


def render_template_to_pdf(template_name, template_vars=None, out_path=None):
    """편의 함수: 템플릿을 PDF로 렌더링"""
    return pdf_renderer.render_template_to_pdf(template_name, template_vars, out_path)


def render_contract_pdf(contract, template_name=None, out_path=None):
    """편의 함수: 계약서 PDF 렌더링"""
    return pdf_renderer.render_contract_pdf(contract, template_name, out_path)
