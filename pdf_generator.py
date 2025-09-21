#!/usr/bin/env python3
"""
PDF 생성 모듈 - ReportLab을 사용한 계약서 PDF 생성
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.colors import black, darkblue, lightgrey
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
from datetime import datetime

class ContractPDFGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.content_width = self.page_width - 2 * self.margin
        
    def generate_contract_pdf(self, contract):
        """계약서 PDF 생성"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # 스타일 정의
        styles = getSampleStyleSheet()
        
        # 제목 스타일
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=darkblue,
            fontName='Helvetica-Bold'
        )
        
        # 섹션 제목 스타일
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=darkblue,
            fontName='Helvetica-Bold'
        )
        
        # 일반 텍스트 스타일
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            fontName='Helvetica'
        )
        
        # 라벨 스타일
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            fontName='Helvetica-Bold',
            textColor=black
        )
        
        # 내용 스타일
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            fontName='Helvetica',
            leftIndent=20
        )
        
        # PDF 내용 구성
        story = []
        
        # 제목
        story.append(Paragraph("부동산 임대차 계약서", title_style))
        story.append(Spacer(1, 20))
        
        # 계약 정보 섹션
        story.append(Paragraph("계약 정보", section_style))
        
        # 고객 정보
        story.append(Paragraph("고객 정보", label_style))
        story.append(Paragraph(f"성명: {contract.customer_name}", content_style))
        story.append(Paragraph(f"연락처: {contract.customer_phone}", content_style))
        story.append(Spacer(1, 10))
        
        # 부동산 정보
        story.append(Paragraph("부동산 정보", label_style))
        story.append(Paragraph(f"주소: {contract.property_address}", content_style))
        story.append(Paragraph(f"임대료: {contract.price:,}원", content_style))
        story.append(Spacer(1, 10))
        
        # 계약 기간
        story.append(Paragraph("계약 기간", label_style))
        story.append(Paragraph(f"시작일: {contract.start_date.strftime('%Y년 %m월 %d일')}", content_style))
        story.append(Paragraph(f"종료일: {contract.end_date.strftime('%Y년 %m월 %d일')}", content_style))
        story.append(Spacer(1, 10))
        
        # 메모
        if contract.memo:
            story.append(Paragraph("특이사항", label_style))
            story.append(Paragraph(contract.memo, content_style))
            story.append(Spacer(1, 10))
        
        # 서명 섹션
        story.append(Spacer(1, 30))
        story.append(Paragraph("서명", section_style))
        
        # 서명 이미지 추가
        if contract.signature_data:
            try:
                # base64 디코딩
                signature_data = contract.signature_data.split(',')[1] if ',' in contract.signature_data else contract.signature_data
                signature_bytes = base64.b64decode(signature_data)
                
                # 서명 이미지 생성
                signature_img = Image(BytesIO(signature_bytes), width=150, height=80)
                signature_img.hAlign = 'RIGHT'
                story.append(signature_img)
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"서명자: {contract.customer_name}", content_style))
            except Exception as e:
                print(f"서명 이미지 처리 오류: {e}")
                story.append(Paragraph("서명: _________________", content_style))
        else:
            story.append(Paragraph("서명: _________________", content_style))
        
        # 계약일
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"계약일: {contract.created_at.strftime('%Y년 %m월 %d일')}", content_style))
        
        # PDF 생성
        doc.build(story)
        
        # PDF 데이터 반환
        buffer.seek(0)
        return buffer.getvalue()
    
    def format_price(self, price):
        """가격 포맷팅"""
        return f"{price:,}원"
