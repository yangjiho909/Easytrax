#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 간단한 PDF 서류 생성 시스템
- 기본적인 PDF 생성 기능
- 한글 지원
- 사용자 양식 적용
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab을 사용할 수 없습니다.")

class SimplePDFGenerator:
    """간단한 PDF 서류 생성기"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self._register_korean_font()
        
    def _register_korean_font(self):
        """한글 폰트 등록"""
        if not REPORTLAB_AVAILABLE:
            return
            
        try:
            # Windows 기본 한글 폰트 경로들
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
                "C:/Windows/Fonts/gulim.ttc",   # 굴림
                "C:/Windows/Fonts/batang.ttc",  # 바탕
                "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 기본 폰트 등록
                        pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                        
                        # Bold 폰트도 같은 폰트로 등록 (대부분의 TTF는 Bold 포함)
                        pdfmetrics.registerFont(TTFont('KoreanFont-Bold', font_path))
                        
                        print(f"✅ 한글 폰트 등록 성공: {font_path}")
                        return
                    except Exception as e:
                        print(f"⚠️ 폰트 등록 실패: {font_path} - {e}")
                        continue
            
            print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        except Exception as e:
            print(f"⚠️ 폰트 등록 중 오류: {e}")
    
    def generate_pdf(self, doc_type: str, data: Dict, output_path: str) -> str:
        """PDF 생성"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_text_fallback(doc_type, data, output_path)
        
        try:
            # PDF 문서 생성
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 제목 스타일 (한글 폰트 적용)
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50'),
                fontName='KoreanFont' if 'KoreanFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
            )
            
            # 제목 추가
            title = Paragraph(f"{doc_type}", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 서류 내용 생성
            content = self._generate_content(doc_type, data)
            story.extend(content)
            
            # PDF 생성
            doc.build(story)
            print(f"✅ PDF 생성 성공: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {e}")
            import traceback
            print(f"📋 상세 오류: {traceback.format_exc()}")
            return self._generate_text_fallback(doc_type, data, output_path)
    
    def _generate_content(self, doc_type: str, data: Dict) -> List:
        """서류 내용 생성"""
        content = []
        
        # 기본 정보
        if 'content' in data:
            # 텍스트 내용 (한글 폰트 적용)
            text_style = ParagraphStyle(
                'CustomText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                fontName='KoreanFont' if 'KoreanFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            content.append(Paragraph(data['content'], text_style))
        
        # 제품 정보 테이블
        if 'product_info' in data or any(key in data for key in ['name', 'code', 'quantity', 'unit_price']):
            table_data = []
            
            # 제품 정보 추출
            product_info = data.get('product_info', {})
            name = product_info.get('name', data.get('name', 'N/A'))
            code = product_info.get('code', data.get('code', 'N/A'))
            quantity = product_info.get('quantity', data.get('quantity', 'N/A'))
            unit_price = product_info.get('unit_price', data.get('unit_price', 'N/A'))
            
            table_data.append(['제품명', name])
            table_data.append(['제품코드', str(code)])
            table_data.append(['수량', str(quantity)])
            table_data.append(['단가', f"${unit_price}"])
            
            # 테이블 생성 (한글 폰트 적용)
            table = Table(table_data, colWidths=[2*inch, 4*inch])
            korean_font = 'KoreanFont' if 'KoreanFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), f'{korean_font}-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), korean_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
            content.append(Spacer(1, 20))
        
        # 생성 날짜 (한글 폰트 적용)
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            fontName='KoreanFont' if 'KoreanFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        )
        content.append(Paragraph(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
        
        return content
    
    def _generate_text_fallback(self, doc_type: str, data: Dict, output_path: str) -> str:
        """텍스트 파일로 대체 생성"""
        try:
            # .pdf 확장자를 .txt로 변경
            txt_path = output_path.replace('.pdf', '.txt')
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {doc_type} ===\n\n")
                
                if 'content' in data:
                    f.write(data['content'])
                    f.write('\n\n')
                
                # 제품 정보
                if 'product_info' in data or any(key in data for key in ['name', 'code', 'quantity', 'unit_price']):
                    f.write("=== 제품 정보 ===\n")
                    product_info = data.get('product_info', {})
                    f.write(f"제품명: {product_info.get('name', data.get('name', 'N/A'))}\n")
                    f.write(f"제품코드: {product_info.get('code', data.get('code', 'N/A'))}\n")
                    f.write(f"수량: {product_info.get('quantity', data.get('quantity', 'N/A'))}\n")
                    f.write(f"단가: ${product_info.get('unit_price', data.get('unit_price', 'N/A'))}\n\n")
                
                f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"✅ 텍스트 파일 생성: {txt_path}")
            return txt_path
            
        except Exception as e:
            print(f"❌ 텍스트 파일 생성 실패: {e}")
            return output_path
    
    def fill_template(self, template_path: str, data: Dict, output_path: str) -> str:
        """사용자 양식에 데이터 채우기"""
        try:
            # 간단한 텍스트 기반 양식 채우기
            if template_path.endswith('.pdf'):
                # PDF 양식은 현재 지원하지 않으므로 기본 PDF 생성
                return self.generate_pdf("사용자 양식", data, output_path)
            else:
                return self._generate_text_fallback("사용자 양식", data, output_path)
        except Exception as e:
            print(f"❌ 양식 채우기 실패: {e}")
            return self.generate_pdf("사용자 양식", data, output_path) 