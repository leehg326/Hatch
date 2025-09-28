#!/usr/bin/env python3
"""
간단한 PDF 테스트
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

def create_simple_pdf():
    """간단한 PDF 생성 테스트"""
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
    
    # 스타일 설정
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=black,
        fontName='Helvetica'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # 내용 추가
    story.append(Paragraph("REAL ESTATE CONTRACT", title_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Document No: TEST_001", normal_style))
    story.append(Paragraph("Contract Date: 2025-01-28", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("1. PARTY INFORMATION", normal_style))
    story.append(Paragraph("Seller: John Doe", normal_style))
    story.append(Paragraph("Buyer: Jane Smith", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("2. PROPERTY INFORMATION", normal_style))
    story.append(Paragraph("Address: 123 Main St, Seoul, Korea", normal_style))
    story.append(Paragraph("Area: 100 sqm", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("3. CONTRACT TERMS", normal_style))
    story.append(Paragraph("Sale Price: KRW 500,000,000", normal_style))
    story.append(Paragraph("Down Payment: KRW 50,000,000", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("4. SIGNATURES", normal_style))
    story.append(Paragraph("Seller: [SIGNATURE]", normal_style))
    story.append(Paragraph("Buyer: [SIGNATURE]", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("5. SECURITY INFORMATION", normal_style))
    story.append(Paragraph("Generated: 2025-01-28 12:00:00", normal_style))
    story.append(Paragraph("Hash: abc123def456...", normal_style))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    pdf_content = create_simple_pdf()
    print(f"PDF 생성 완료: {len(pdf_content)} bytes")
    
    # 파일로 저장
    with open("test_simple.pdf", "wb") as f:
        f.write(pdf_content)
    print("PDF 파일 저장: test_simple.pdf")

