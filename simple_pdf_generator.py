#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 간단한 PDF 생성기
- 좌표 기반 PDF 생성기가 없을 때 사용하는 백업 옵션
- 기본적인 텍스트 기반 PDF 생성
"""

import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_simple_pdf(content: str, output_path: str, doc_name: str):
    """간단한 PDF 생성"""
    try:
        # 한글 폰트 등록
        _register_korean_font()
        
        # PDF 생성
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # 제목
        c.setFont("KoreanFont", 16)
        c.drawString(50, height - 50, f"{doc_name}")
        
        # 구분선
        c.line(50, height - 70, width - 50, height - 70)
        
        # 내용
        c.setFont("KoreanFont", 10)
        y_position = height - 100
        
        # 내용을 줄별로 분할
        lines = content.split('\n')
        for line in lines:
            if y_position < 50:  # 페이지 끝에 도달하면 새 페이지
                c.showPage()
                y_position = height - 50
                c.setFont("KoreanFont", 10)
            
            # 긴 줄은 자동 줄바꿈
            if len(line) > 80:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) < 80:
                        current_line += word + " "
                    else:
                        c.drawString(50, y_position, current_line.strip())
                        y_position -= 15
                        current_line = word + " "
                if current_line:
                    c.drawString(50, y_position, current_line.strip())
                    y_position -= 15
            else:
                c.drawString(50, y_position, line)
                y_position -= 15
        
        # 생성 정보
        c.setFont("KoreanFont", 8)
        c.drawString(50, 30, f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 15, f"문서유형: {doc_name}")
        
        c.save()
        print(f"✅ 간단한 PDF 생성 완료: {output_path}")
        
    except Exception as e:
        print(f"❌ 간단한 PDF 생성 실패: {e}")
        # 텍스트 파일로 대체
        txt_path = output_path.replace('.pdf', '.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {doc_name} ===\n\n{content}")
        print(f"📄 텍스트 파일로 대체: {txt_path}")

def _register_korean_font():
    """한글 폰트 등록"""
    try:
        # 한글 폰트 경로들
        korean_fonts = [
            "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
            "C:/Windows/Fonts/gulim.ttc",       # 굴림
            "/System/Library/Fonts/AppleGothic.ttf",  # macOS
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # Linux
        ]
        
        for font_path in korean_fonts:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                print(f"✅ 한글 폰트 등록 성공: {font_path}")
                return
        
        print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        
    except Exception as e:
        print(f"❌ 폰트 등록 실패: {e}")

class SimplePDFGenerator:
    """간단한 PDF 생성기 클래스"""
    
    def __init__(self):
        self.font_registered = False
    
    def generate_pdf(self, content: str, output_path: str, doc_name: str):
        """PDF 생성 메서드"""
        return generate_simple_pdf(content, output_path, doc_name)
    
    def generate_commercial_invoice(self, data: dict, output_path: str):
        """상업송장 생성"""
        content = self._format_commercial_invoice(data)
        return self.generate_pdf(content, output_path, "상업송장")
    
    def generate_packing_list(self, data: dict, output_path: str):
        """포장명세서 생성"""
        content = self._format_packing_list(data)
        return self.generate_pdf(content, output_path, "포장명세서")
    
    def _format_commercial_invoice(self, data: dict) -> str:
        """상업송장 형식"""
        content = f"""
상업송장 (Commercial Invoice)

제조사/수출자 (Manufacturer/Exporter):
{data.get('manufacturer', 'N/A')}

수입자 (Importer):
{data.get('importer', 'N/A')}

운송수단 (Means of Transport):
{data.get('transport', 'N/A')}

상품명 (Description of Goods):
{data.get('product_name', 'N/A')}

수량 (Quantity):
{data.get('quantity', 'N/A')}

단가 (Unit Price):
{data.get('unit_price', 'N/A')}

총액 (Total Amount):
{data.get('total_amount', 'N/A')}

원산지 (Country of Origin):
{data.get('origin', 'N/A')}

HS코드 (HS Code):
{data.get('hs_code', 'N/A')}

생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return content.strip()
    
    def _format_packing_list(self, data: dict) -> str:
        """포장명세서 형식"""
        content = f"""
포장명세서 (Packing List)

제조사/수출자 (Manufacturer/Exporter):
{data.get('manufacturer', 'N/A')}

수입자 (Importer):
{data.get('importer', 'N/A')}

운송수단 (Means of Transport):
{data.get('transport', 'N/A')}

상품명 (Description of Goods):
{data.get('product_name', 'N/A')}

포장수량 (Number of Packages):
{data.get('package_count', 'N/A')}

총 중량 (Gross Weight):
{data.get('gross_weight', 'N/A')}

순 중량 (Net Weight):
{data.get('net_weight', 'N/A')}

부피 (Volume):
{data.get('volume', 'N/A')}

포장방법 (Packing Method):
{data.get('packing_method', 'N/A')}

생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return content.strip()
        print(f"⚠️ 폰트 등록 실패: {e}")

if __name__ == "__main__":
    # 테스트
    test_content = """
상업송장 (Commercial Invoice)

판매자: 테스트 회사
구매자: 테스트 구매자
제품명: 테스트 라면
수량: 1000개
단가: $1.00
총액: $1,000.00

이 문서는 테스트용으로 생성되었습니다.
"""
    
    generate_simple_pdf(test_content, "test_invoice.pdf", "상업송장") 