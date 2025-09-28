#!/usr/bin/env python3
"""
간단하고 안정적인 PDF 생성기 - ReportLab 기반
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.colors import black, darkblue, lightgrey, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.cidfonts import CIDFont
from io import BytesIO
import os
from datetime import datetime
import qrcode

class SimpleContractPDF:
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정 - 다중 방법 시도"""
        try:
            # 방법 1: UnicodeCIDFont 사용 (한글 지원)
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
                self.font_name = 'HeiseiKakuGo-W5'
                print("UnicodeCIDFont 등록 성공: HeiseiKakuGo-W5")
                return
            except Exception as e:
                print(f"UnicodeCIDFont 등록 실패: {e}")
            
            # 방법 2: 다른 CID 폰트 시도
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
                self.font_name = 'HeiseiMin-W3'
                print("UnicodeCIDFont 등록 성공: HeiseiMin-W3")
                return
            except Exception as e:
                print(f"HeiseiMin-W3 등록 실패: {e}")
            
            # 방법 3: Windows 한글 폰트 시도
            if os.name == 'nt':
                font_candidates = [
                    ('C:/Windows/Fonts/malgun.ttf', 'MalgunGothic'),
                    ('C:/Windows/Fonts/gulim.ttc', 'Gulim'),
                    ('C:/Windows/Fonts/batang.ttc', 'Batang'),
                    ('C:/Windows/Fonts/dotum.ttc', 'Dotum')
                ]
                
                self.font_name = 'Helvetica'  # 기본값
                
                for font_path, font_name in font_candidates:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            self.font_name = font_name
                            print(f"한글 폰트 등록 성공: {font_name}")
                            break
                        except Exception as e:
                            print(f"폰트 등록 실패 {font_name}: {e}")
                            continue
                
                if self.font_name == 'Helvetica':
                    print("한글 폰트 등록 실패, Helvetica 사용")
            else:
                self.font_name = 'Helvetica'
        except Exception as e:
            print(f"폰트 설정 실패: {e}")
            self.font_name = 'Helvetica'
    
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
        
        # 테이블 헤더 스타일
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            fontName=self.font_name,
            alignment=TA_CENTER
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
        """계약서 PDF 생성"""
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
        contract_type_korean = {
            'SALE': '매매',
            'JEONSE': '전세', 
            'WOLSE': '월세'
        }.get(contract.type.value, contract.type.value)
        
        title = f"부동산 {contract_type_korean}계약서"
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 2. 문서 정보
        doc_info = f"문서번호: {contract.doc_no} | 계약일: {contract.contract_date or '미정'}"
        story.append(Paragraph(doc_info, self.normal_style))
        story.append(Spacer(1, 20))
        
        # 3. 당사자 정보
        story.append(Paragraph("1. 당사자 인적사항", self.section_style))
        
        party_data = [
            ['구분', '성명', '연락처'],
            ['매도인/임대인', contract.seller_name, contract.seller_phone],
            ['매수인/임차인', contract.buyer_name, contract.buyer_phone]
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
        story.append(Paragraph("2. 부동산의 표시", self.section_style))
        
        property_data = [
            ['소재지', contract.property_address],
            ['구조/면적', contract.unit.get('structure', '') + ' / ' + contract.unit.get('area', '') + '㎡' if contract.unit else ''],
            ['용도', '주거용']
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
        story.append(Paragraph("3. 계약 조건", self.section_style))
        
        if contract.type.value == 'SALE':
            # 매매계약
            price_data = [
                ['매매가격', f"{contract.sale_price:,}원" if contract.sale_price else ''],
                ['계약금', f"{int(contract.sale_price * 0.1):,}원" if contract.sale_price else ''],
                ['중도금', f"{int(contract.sale_price * 0.4):,}원" if contract.sale_price else ''],
                ['잔금', f"{int(contract.sale_price * 0.5):,}원" if contract.sale_price else '']
            ]
        elif contract.type.value == 'JEONSE':
            # 전세계약
            price_data = [
                ['전세금', f"{contract.deposit:,}원" if contract.deposit else ''],
                ['계약기간', f"{contract.contract_date} ~ {contract.handover_date}" if contract.contract_date and contract.handover_date else '']
            ]
        else:  # WOLSE
            # 월세계약
            price_data = [
                ['보증금', f"{contract.deposit:,}원" if contract.deposit else ''],
                ['월차임', f"{contract.monthly_rent:,}원" if contract.monthly_rent else ''],
                ['계약기간', f"{contract.contract_date} ~ {contract.handover_date}" if contract.contract_date and contract.handover_date else '']
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
            story.append(Paragraph("4. 특약사항", self.section_style))
            story.append(Paragraph(contract.special_terms, self.normal_style))
            story.append(Spacer(1, 15))
        
        # 7. 서명란
        story.append(Paragraph("5. 서명 및 날인", self.section_style))
        
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
                ('매도인', 'SELLER'),
                ('매수인', 'BUYER'),
                ('중개인', 'AGENT')
            ]
        else:  # JEONSE, WOLSE
            roles = [
                ('임대인', 'LESSOR'),
                ('임차인', 'LESSEE'),
                ('중개인', 'BROKER')
            ]
        
        signature_data = [['구분', '서명', '날짜']]
        for role_name, role_key in roles:
            sig = signature_dict.get(role_key)
            if sig and sig.signed_at:
                signature_data.append([role_name, '✓ 서명완료', sig.signed_at.strftime('%Y-%m-%d')])
            else:
                signature_data.append([role_name, '□ 서명대기', ''])
        
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
        story.append(Paragraph("6. 보안 정보", self.section_style))
        
        # QR 코드 생성
        qr_buffer = self.create_qr_code(contract.id, contract.doc_hash)
        if qr_buffer:
            qr_img = Image(qr_buffer, width=50, height=50)
            story.append(qr_img)
        
        # 보안 정보
        security_info = f"""
        문서번호: {contract.doc_no}
        생성일: {contract.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        해시: {contract.doc_hash[:16] if contract.doc_hash else 'N/A'}...
        """
        story.append(Paragraph(security_info, self.normal_style))
        
        # PDF 생성
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
