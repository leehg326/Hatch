#!/usr/bin/env python3
"""
PDF 생성 모듈 - ReportLab을 사용한 계약서 PDF 생성
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.colors import black, darkblue, lightgrey, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64
from datetime import datetime
import os

class ContractPDFGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.content_width = self.page_width - 2 * self.margin
        
        # 한글 폰트 등록 (시스템에 따라 경로 조정 필요)
        try:
            # Windows 기본 한글 폰트
            if os.name == 'nt':
                pdfmetrics.registerFont(TTFont('HYSMyeongJo', 'C:/Windows/Fonts/malgun.ttf'))
            else:
                # Linux/Mac 기본 한글 폰트
                pdfmetrics.registerFont(TTFont('HYSMyeongJo', '/System/Library/Fonts/AppleGothic.ttf'))
        except:
            # 폰트 등록 실패 시 기본 폰트 사용
            print("한글 폰트 등록 실패, 기본 폰트 사용")
        
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
    
    def generate_sale_contract_pdf(self, contract):
        """표준 부동산 매매계약서 PDF 생성 (한국공인중개사협회 표준양식)"""
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
            'SaleTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=black,
            fontName='HYSMyeongJo'
        )
        
        # 섹션 제목 스타일
        section_style = ParagraphStyle(
            'SaleSection',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=black,
            fontName='HYSMyeongJo'
        )
        
        # 일반 텍스트 스타일
        normal_style = ParagraphStyle(
            'SaleNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='HYSMyeongJo'
        )
        
        # 테이블 스타일
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'HYSMyeongJo'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ])
        
        # PDF 내용 구성
        story = []
        
        # 제목
        story.append(Paragraph("부동산 매매계약서", title_style))
        story.append(Spacer(1, 20))
        
        # 1. 당사자 인적사항
        story.append(Paragraph("1. 당사자 인적사항", section_style))
        
        # 매수인 정보
        buyer_data = [
            ['구분', '성명', '주민등록번호', '주소', '연락처'],
            ['매수인', contract.buyer_name, '_________________', '_________________', contract.buyer_phone]
        ]
        buyer_table = Table(buyer_data, colWidths=[60, 80, 120, 150, 100])
        buyer_table.setStyle(table_style)
        story.append(buyer_table)
        story.append(Spacer(1, 15))
        
        # 매도인 정보
        seller_data = [
            ['구분', '성명', '주민등록번호', '주소', '연락처'],
            ['매도인', contract.seller_name, '_________________', '_________________', contract.seller_phone]
        ]
        seller_table = Table(seller_data, colWidths=[60, 80, 120, 150, 100])
        seller_table.setStyle(table_style)
        story.append(seller_table)
        story.append(Spacer(1, 20))
        
        # 2. 물건 표시
        story.append(Paragraph("2. 물건 표시", section_style))
        
        property_data = [
            ['구분', '내용'],
            ['소재지', contract.property_address],
            ['면적', '_________________'],
            ['지목', '_________________'],
            ['지번', '_________________'],
            ['건물구조', '_________________'],
            ['건물면적', '_________________']
        ]
        property_table = Table(property_data, colWidths=[80, 400])
        property_table.setStyle(table_style)
        story.append(property_table)
        story.append(Spacer(1, 20))
        
        # 3. 계약 조건
        story.append(Paragraph("3. 계약 조건", section_style))
        
        # 매매금액
        story.append(Paragraph(f"매매금액: {self.format_price(contract.sale_price)}", normal_style))
        story.append(Spacer(1, 10))
        
        # 계약금, 중도금, 잔금 테이블
        payment_data = [
            ['구분', '금액', '지급일', '비고'],
            ['계약금', self.format_price(contract.contract_deposit), contract.contract_date.strftime('%Y년 %m월 %d일'), ''],
            ['중도금', self.format_price(contract.intermediate_payment), '_________________', ''],
            ['잔금', self.format_price(contract.final_payment), contract.final_payment_date.strftime('%Y년 %m월 %d일'), '']
        ]
        payment_table = Table(payment_data, colWidths=[80, 120, 150, 100])
        payment_table.setStyle(table_style)
        story.append(payment_table)
        story.append(Spacer(1, 15))
        
        # 인도일
        story.append(Paragraph(f"인도일: {contract.delivery_date.strftime('%Y년 %m월 %d일')}", normal_style))
        story.append(Spacer(1, 20))
        
        # 4. 특약사항
        story.append(Paragraph("4. 특약사항", section_style))
        
        special_terms = [
            "1. 매도인은 매수인에게 위 물건을 매매계약 체결일로부터 30일 이내에 인도한다.",
            "2. 매도인은 매수인에게 위 물건의 소유권을 이전하고, 매수인은 매도인에게 매매대금을 지급한다.",
            "3. 매도인은 위 물건에 대한 권리상의 하자가 없음을 보증한다.",
            "4. 기타 특약사항:",
            "   _________________________________________________",
            "   _________________________________________________"
        ]
        
        for term in special_terms:
            story.append(Paragraph(term, normal_style))
        
        story.append(Spacer(1, 30))
        
        # 5. 서명란
        story.append(Paragraph("5. 서명", section_style))
        
        signature_data = [
            ['매수인', '매도인'],
            ['(서명)', '(서명)'],
            ['', ''],
            ['', ''],
            ['', '']
        ]
        signature_table = Table(signature_data, colWidths=[200, 200])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'HYSMyeongJo'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 20))
        
        # 계약일
        story.append(Paragraph(f"계약일: {contract.contract_date.strftime('%Y년 %m월 %d일')}", normal_style))
        
        # PDF 생성
        doc.build(story)
        
        # PDF 데이터 반환
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_rental_contract_pdf(self, contract):
        """임대차계약서 PDF 생성 (기존 메서드 이름 변경)"""
        return self.generate_contract_pdf(contract)
    
    def format_price(self, price):
        """가격 포맷팅"""
        return f"{price:,}원"
