# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, darkblue, darkred
from io import BytesIO
import qrcode
from datetime import datetime
import os

class StandardContractPDF:
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정"""
        try:
            # Noto Sans CJK 폰트 등록 (폰트 파일이 있는 경우)
            font_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'NotoSansCJK-Regular.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('NotoSansCJK', font_path))
                self.font_name = 'NotoSansCJK'
            else:
                # 기본 폰트 사용
                self.font_name = 'Helvetica'
        except:
            self.font_name = 'Helvetica'
    
    def setup_styles(self):
        """스타일 설정"""
        self.styles = getSampleStyleSheet()
        
        # 제목 스타일
        if 'ContractTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ContractTitle',
                parent=self.styles['Heading1'],
                fontName=self.font_name,
                fontSize=16,
                spaceAfter=12,
                alignment=TA_CENTER,
                textColor=darkblue
            ))
        
        # 섹션 제목 스타일
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=6,
                spaceBefore=12,
                textColor=darkred
            ))
        
        # 본문 스타일
        if 'ContractBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ContractBodyText',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            ))
        
        # 테이블 헤더 스타일
        if 'TableHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.white
            ))
        
        # 테이블 내용 스타일
        if 'TableCell' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableCell',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                alignment=TA_LEFT
            ))
    
    def format_currency(self, amount):
        """금액 포맷팅"""
        if amount is None:
            return "해당 없음"
        return f"￦{amount:,}"
    
    def format_date(self, date_obj):
        """날짜 포맷팅"""
        if date_obj is None:
            return "해당 없음"
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            except:
                return date_obj
        return f"{date_obj.year}년 {date_obj.month}월 {date_obj.day}일"
    
    def get_contract_type_korean(self, contract_type):
        """계약 유형 한글 변환"""
        type_map = {
            'SALE': '매매',
            'JEONSE': '전세',
            'WOLSE': '월세',
            'BANJEONSE': '반전세'
        }
        return type_map.get(contract_type, contract_type)
    
    def create_qr_code(self, doc_no):
        """QR 코드 생성"""
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(f"https://example.com/contracts/verify?doc={doc_no}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        return qr_buffer
    
    def generate_contract_pdf(self, contract, include_signatures=False, include_stamps=False):
        """계약서 PDF 생성"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18*mm,
            leftMargin=18*mm,
            topMargin=18*mm,
            bottomMargin=18*mm
        )
        
        story = []
        
        # 1. 머리말
        contract_type_korean = self.get_contract_type_korean(contract.type.value)
        title = f"부동산 {contract_type_korean} 계약서"
        story.append(Paragraph(title, self.styles['ContractTitle']))
        
        # 문서 정보
        doc_info = f"문서번호: {contract.doc_no} | 생성일: {self.format_date(contract.created_at)}"
        story.append(Paragraph(doc_info, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 2. 당사자 인적사항
        story.append(Paragraph("1. 당사자 인적사항", self.styles['SectionTitle']))
        
        party_data = [
            ['구분', '성명', '연락처', '주소'],
            ['매도인/임대인', contract.seller_name, contract.seller_phone, contract.property_address],
            ['매수인/임차인', contract.buyer_name, contract.buyer_phone, contract.property_address]
        ]
        
        party_table = Table(party_data, colWidths=[30*mm, 40*mm, 40*mm, 60*mm])
        party_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(party_table)
        story.append(Spacer(1, 12))
        
        # 3. 부동산의 표시
        story.append(Paragraph("2. 부동산의 표시", self.styles['SectionTitle']))
        
        property_data = [
            ['소재지', contract.property_address],
            ['면적', contract.unit.get('area', '해당 없음') if contract.unit else '해당 없음'],
            ['구조/용도', contract.unit.get('structure', '해당 없음') if contract.unit else '해당 없음']
        ]
        
        property_table = Table(property_data, colWidths=[30*mm, 140*mm])
        property_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(property_table)
        story.append(Spacer(1, 12))
        
        # 4. 계약금액/지급조건
        story.append(Paragraph("3. 계약금액 및 지급조건", self.styles['SectionTitle']))
        
        if contract.type.value == 'SALE':
            # 매매 계약
            schedule = contract.schedule or {}
            amount_data = [
                ['구분', '금액', '지급일'],
                ['계약금', self.format_currency(contract.price_total * 0.1 if contract.price_total else 0), 
                 self.format_date(schedule.get('contract_date'))],
                ['중도금', self.format_currency(contract.price_total * 0.4 if contract.price_total else 0), 
                 self.format_date(schedule.get('middle_date'))],
                ['잔금', self.format_currency(contract.price_total * 0.5 if contract.price_total else 0), 
                 self.format_date(schedule.get('balance_date'))],
                ['총 매매가격', self.format_currency(contract.price_total), '']
            ]
        elif contract.type.value == 'JEONSE':
            # 전세 계약
            schedule = contract.schedule or {}
            amount_data = [
                ['구분', '금액', '지급일'],
                ['보증금', self.format_currency(contract.deposit), 
                 self.format_date(schedule.get('balance_date'))],
                ['월세', '해당 없음', '']
            ]
        else:
            # 월세/반전세 계약
            amount_data = [
                ['구분', '금액', '지급일'],
                ['보증금', self.format_currency(contract.deposit), '계약일'],
                ['월차임', self.format_currency(contract.monthly_rent), f'매월 {contract.monthly_payday}일'],
                ['관리비', self.format_currency(contract.mgmt_fee) if contract.mgmt_fee else '해당 없음', 
                 f'매월 {contract.monthly_payday}일' if contract.mgmt_fee else '']
            ]
        
        amount_table = Table(amount_data, colWidths=[40*mm, 50*mm, 50*mm])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(amount_table)
        story.append(Spacer(1, 12))
        
        # 5. 소유권 이전/인도
        story.append(Paragraph("4. 소유권 이전 및 인도", self.styles['SectionTitle']))
        
        schedule = contract.schedule or {}
        transfer_text = f"""
        등기 및 인도일: {self.format_date(schedule.get('transfer_date'))}<br/>
        인도 범위: 열쇠, 설비, 비품 등 계약 목적물 전부
        """
        story.append(Paragraph(transfer_text, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 6. 권리관계 및 하자담보
        story.append(Paragraph("5. 권리관계 및 하자담보", self.styles['SectionTitle']))
        
        rights_text = """
        • 근저당권, 가압류 등 권리관계는 매수인이 인수하며, 매도인은 계약일로부터 60일 이내에 말소하여야 합니다.<br/>
        • 하자 발견 시 매도인은 즉시 수리하거나 손해를 배상하여야 합니다.
        """
        story.append(Paragraph(rights_text, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 7. 공과금 및 관리비 정산
        story.append(Paragraph("6. 공과금 및 관리비 정산", self.styles['SectionTitle']))
        
        utility_text = """
        • 공과금 정산 기준일: 인도일<br/>
        • 관리비: 매월 지급일 기준으로 정산<br/>
        • 미납 공과금이 있는 경우 매도인이 부담하여야 합니다.
        """
        story.append(Paragraph(utility_text, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 8. 중개사무소 정보
        story.append(Paragraph("7. 중개사무소", self.styles['SectionTitle']))
        
        brokerage = contract.brokerage or {}
        brokerage_text = f"""
        상호: {brokerage.get('office_name', '해당 없음')}<br/>
        대표자: {brokerage.get('rep', '해당 없음')}<br/>
        등록번호: {brokerage.get('reg_no', '해당 없음')}<br/>
        소재지: {brokerage.get('address', '해당 없음')}<br/>
        연락처: {brokerage.get('phone', '해당 없음')}<br/>
        <br/>
        ※ 중개대상물 확인·설명서를 교부받았음을 확인합니다.
        """
        story.append(Paragraph(brokerage_text, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 9. 중개보수 및 실비
        story.append(Paragraph("8. 중개보수 및 실비", self.styles['SectionTitle']))
        
        fee_text = f"""
        중개보수: {brokerage.get('fee', '해당 없음')}<br/>
        실비: {brokerage.get('fee_note', '해당 없음')}<br/>
        <br/>
        ※ 중개보수는 계약 체결 시 지급하며, 실비는 별도로 정산합니다.
        """
        story.append(Paragraph(fee_text, self.styles['ContractBodyText']))
        story.append(Spacer(1, 12))
        
        # 10. 특약사항
        if contract.special_terms:
            story.append(Paragraph("9. 특약사항", self.styles['SectionTitle']))
            story.append(Paragraph(contract.special_terms, self.styles['ContractBodyText']))
            story.append(Spacer(1, 12))
        
        # 11. 서명란
        story.append(Paragraph("10. 서명 및 날인", self.styles['SectionTitle']))
        
        signature_data = [
            ['구분', '서명/날인', '날짜'],
            ['매도인/임대인', '_________________', '_________________'],
            ['매수인/임차인', '_________________', '_________________'],
            ['개업공인중개사', '_________________', '_________________']
        ]
        
        signature_table = Table(signature_data, colWidths=[40*mm, 60*mm, 40*mm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 20))
        
        # 12. 하단 증빙 정보
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.grey))
        
        # QR 코드 및 문서 정보
        try:
            qr_buffer = self.create_qr_code(contract.doc_no)
            from reportlab.platypus import Image
            qr_img = Image(qr_buffer, width=20*mm, height=20*mm)
            
            footer_data = [
                [qr_img, f"문서번호: {contract.doc_no}"],
                ['', f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}"],
                ['', f"문서해시: {contract.get_short_hash()}"],
                ['', f"양식버전: {contract.form_version}"]
            ]
            
            footer_table = Table(footer_data, colWidths=[25*mm, 115*mm])
            footer_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(footer_table)
        except:
            # QR 코드 생성 실패 시 텍스트만 표시
            footer_text = f"""
            문서번호: {contract.doc_no} | 생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}<br/>
            문서해시: {contract.get_short_hash()} | 양식버전: {contract.form_version}
            """
            story.append(Paragraph(footer_text, self.styles['ContractBodyText']))
        
        # 서명 섹션 (옵션)
        if include_signatures and hasattr(contract, 'signatures') and contract.signatures:
            story.append(Spacer(1, 20))
            story.append(Paragraph("서명", self.styles['SectionTitle']))
            
            # 서명 이미지 포함 테이블 생성
            from reportlab.platypus import Image as ReportLabImage
            import os
            
            signature_data = [['구분', '서명', '서명일시']]
            
            for sig in contract.signatures:
                role_korean = {
                    'SELLER': '매도인/임대인',
                    'BUYER': '매수인/임차인', 
                    'AGENT': '중개인'
                }.get(sig.role.value, sig.role.value)
                
                signed_date = sig.signed_at.strftime('%Y년 %m월 %d일') if sig.signed_at else '미서명'
                
                # 서명 이미지가 있는 경우
                if hasattr(sig, 'image_path') and sig.image_path and os.path.exists(sig.image_path):
                    try:
                        # 서명 이미지 로드 (크기 조정)
                        sig_img = ReportLabImage(sig.image_path, width=60*mm, height=30*mm)
                        signature_data.append([role_korean, sig_img, signed_date])
                    except:
                        signature_data.append([role_korean, '[서명 이미지 오류]', signed_date])
                else:
                    signature_data.append([role_korean, '[서명 대기]', signed_date])
            
            signature_table = Table(signature_data, colWidths=[50*mm, 60*mm, 50*mm])
            signature_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(signature_table)
            story.append(Spacer(1, 12))
        
        # 면책 조항
        disclaimer = """
        <br/>
        ※ 본 계약서는 한국공인중개사협회 표준계약서 형식을 준용하였습니다.<br/>
        ※ 개별 사안은 당사자 합의 및 관련 법령을 우선합니다.<br/>
        ※ 본 문서는 법률자문이 아니며, 필요시 전문가와 상담하시기 바랍니다.
        """
        story.append(Paragraph(disclaimer, self.styles['ContractBodyText']))
        
        # PDF 생성
        doc.build(story)
        buffer.seek(0)
        
        return buffer
