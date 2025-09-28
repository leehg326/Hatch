#!/usr/bin/env python3
"""
한글 폰트 문제 해결을 위한 새로운 PDF 생성기
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.colors import black, darkblue, lightgrey, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from datetime import datetime
import qrcode

class SimpleContractPDFV2:
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정 - 최소한의 안전한 방법"""
        # 기본 Helvetica 폰트 사용 (한글 문제 회피)
        self.font_name = 'Helvetica'
        print("Helvetica 폰트 사용 (한글 문제 회피)")
    
    def setup_styles(self):
        """스타일 설정"""
        styles = getSampleStyleSheet()
        
        # 제목 스타일
        self.title_style = ParagraphStyle(
            'ContractTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black,
            fontName=self.font_name
        )
        
        # 섹션 제목 스타일
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=black,
            fontName=self.font_name
        )
        
        # 일반 텍스트 스타일
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName=self.font_name
        )
    
    def create_qr_code(self, contract_id, doc_hash):
        """QR 코드 생성"""
        try:
            qr_data = f"CONTRACT_ID:{contract_id}|HASH:{doc_hash[:16] if doc_hash else 'N/A'}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=1,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # PIL Image를 BytesIO로 변환
            img_buffer = BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
        except Exception as e:
            print(f"QR 코드 생성 실패: {e}")
            return None
    
    def generate_contract_pdf(self, contract):
        """계약서 PDF 생성 - 영어 버전"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # 1. 제목
        contract_type_english = {
            'SALE': 'SALE',
            'JEONSE': 'JEONSE', 
            'WOLSE': 'RENTAL'
        }.get(contract.type.value, contract.type.value)
        
        title = f"REAL ESTATE {contract_type_english} CONTRACT"
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 2. 문서 정보
        doc_info = f"Document No: {contract.doc_no} | Contract Date: {contract.contract_date or 'TBD'}"
        story.append(Paragraph(doc_info, self.normal_style))
        story.append(Spacer(1, 20))
        
        # 3. 당사자 정보
        story.append(Paragraph("1. PARTY INFORMATION", self.section_style))
        
        party_data = [
            ['Role', 'Name', 'Phone'],
            ['Seller/Lessor', contract.seller_name or 'N/A', contract.seller_phone or 'N/A'],
            ['Buyer/Lessee', contract.buyer_name or 'N/A', contract.buyer_phone or 'N/A']
        ]
        
        party_table = Table(party_data, colWidths=[40*mm, 60*mm, 60*mm])
        party_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        story.append(party_table)
        story.append(Spacer(1, 15))
        
        # 4. 부동산 정보
        story.append(Paragraph("2. PROPERTY INFORMATION", self.section_style))
        
        property_data = [
            ['Address', contract.property_address or 'N/A'],
            ['Structure/Area', contract.unit.get('structure', '') + ' / ' + contract.unit.get('area', '') + 'sqm' if contract.unit else 'N/A'],
            ['Usage', 'Residential']
        ]
        
        property_table = Table(property_data, colWidths=[40*mm, 120*mm])
        property_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        story.append(property_table)
        story.append(Spacer(1, 15))
        
        # 5. 계약 조건
        story.append(Paragraph("3. CONTRACT TERMS", self.section_style))
        
        if contract.type.value == 'SALE':
            # 매매계약
            price_data = [
                ['Sale Price', f"KRW {contract.sale_price:,}" if contract.sale_price else 'N/A'],
                ['Down Payment', f"KRW {int(contract.sale_price * 0.1):,}" if contract.sale_price else 'N/A'],
                ['Interim Payment', f"KRW {int(contract.sale_price * 0.4):,}" if contract.sale_price else 'N/A'],
                ['Final Payment', f"KRW {int(contract.sale_price * 0.5):,}" if contract.sale_price else 'N/A']
            ]
        elif contract.type.value == 'JEONSE':
            # 전세계약
            price_data = [
                ['Jeonse Deposit', f"KRW {contract.deposit:,}" if contract.deposit else 'N/A'],
                ['Contract Period', f"{contract.contract_date} ~ {contract.handover_date}" if contract.contract_date and contract.handover_date else 'N/A']
            ]
        else:  # WOLSE
            # 월세계약
            price_data = [
                ['Security Deposit', f"KRW {contract.deposit:,}" if contract.deposit else 'N/A'],
                ['Monthly Rent', f"KRW {contract.monthly_rent:,}" if contract.monthly_rent else 'N/A'],
                ['Contract Period', f"{contract.contract_date} ~ {contract.handover_date}" if contract.contract_date and contract.handover_date else 'N/A']
            ]
        
        price_table = Table(price_data, colWidths=[40*mm, 120*mm])
        price_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        story.append(price_table)
        story.append(Spacer(1, 15))
        
        # 6. 특약사항
        if contract.special_terms:
            story.append(Paragraph("4. SPECIAL TERMS", self.section_style))
            story.append(Paragraph(contract.special_terms, self.normal_style))
            story.append(Spacer(1, 15))
        
        # 7. 서명란
        story.append(Paragraph("5. SIGNATURES", self.section_style))
        
        # 서명 정보 로드
        try:
            from models import ContractSignature
            signatures = ContractSignature.query.filter_by(contract_id=contract.id).all()
            signature_dict = {sig.role.value: sig for sig in signatures}
        except:
            signature_dict = {}
        
        # 계약 유형에 따른 서명 역할
        if contract.type.value == 'SALE':
            roles = [
                ('Seller', 'SELLER'),
                ('Buyer', 'BUYER'),
                ('Agent', 'AGENT')
            ]
        else:  # JEONSE, WOLSE
            roles = [
                ('Lessor', 'LESSOR'),
                ('Lessee', 'LESSEE'),
                ('Broker', 'BROKER')
            ]
        
        signature_data = [['Role', 'Signature', 'Date']]
        for role_name, role_key in roles:
            sig = signature_dict.get(role_key)
            if sig and sig.signed_at:
                signature_data.append([role_name, 'SIGNED', sig.signed_at.strftime('%Y-%m-%d')])
            else:
                signature_data.append([role_name, 'PENDING', ''])
        
        signature_table = Table(signature_data, colWidths=[40*mm, 60*mm, 60*mm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('BACKGROUND', (0, 0), (-1, 0), lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, lightgrey])
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 20))
        
        # 8. QR 코드 및 보안 정보
        story.append(Paragraph("6. SECURITY INFORMATION", self.section_style))
        
        # QR 코드 생성
        qr_buffer = self.create_qr_code(contract.id, contract.doc_hash)
        if qr_buffer:
            qr_img = Image(qr_buffer, width=50, height=50)
            story.append(qr_img)
        
        # 보안 정보
        security_info = f"""
        Document No: {contract.doc_no}
        Generated: {contract.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        Hash: {contract.doc_hash[:16] if contract.doc_hash else 'N/A'}...
        """
        story.append(Paragraph(security_info, self.normal_style))
        
        # PDF 생성
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

