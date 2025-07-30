#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 고도화된 PDF 서류 생성 시스템
- 자유 양식 vs 규정 양식 구분 처리
- 시각적 품질 및 사용자 설정 지원
- 양식 버전 관리 및 업데이트 시스템
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import base64

# PDF 생성 라이브러리들
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab을 사용할 수 없습니다. FPDF2를 사용합니다.")

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️ FPDF2를 사용할 수 없습니다.")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("⚠️ PyPDF2를 사용할 수 없습니다.")

class FormType(Enum):
    """서류 양식 유형"""
    FREE = "free"           # 자유 양식 (상업송장, 포장명세서)
    REGULATED = "regulated" # 규정 양식 (원산지증명서, 검역증명서)
    HYBRID = "hybrid"       # 혼합 양식 (일부 자유, 일부 규정)

class DocumentTemplate:
    """서류 템플릿 클래스"""
    
    def __init__(self, name: str, form_type: FormType, version: str = "1.0"):
        self.name = name
        self.form_type = form_type
        self.version = version
        self.created_date = datetime.now()
        self.last_updated = datetime.now()
        self.required_fields = []
        self.optional_fields = []
        self.layout_settings = {}
        self.styling = {}
        
    def to_dict(self) -> Dict:
        """템플릿을 딕셔너리로 변환"""
        return {
            "name": self.name,
            "form_type": self.form_type.value,
            "version": self.version,
            "created_date": self.created_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "required_fields": self.required_fields,
            "optional_fields": self.optional_fields,
            "layout_settings": self.layout_settings,
            "styling": self.styling
        }

class AdvancedPDFGenerator:
    """고도화된 PDF 서류 생성기"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.form_templates = self._load_form_templates()
        self.customization_options = self._load_customization_options()
        
        # 폰트 등록 (한글 지원)
        self._register_fonts()
        
    def _register_fonts(self):
        """한글 폰트 등록"""
        if REPORTLAB_AVAILABLE:
            try:
                # 한글 폰트 경로들
                korean_fonts = [
                    "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
                    "C:/Windows/Fonts/gulim.ttc",       # 굴림
                    "C:/Windows/Fonts/msyh.ttc",        # Microsoft YaHei
                    "/System/Library/Fonts/AppleGothic.ttf",  # macOS
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # Linux
                ]
                
                for font_path in korean_fonts:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                        print(f"✅ 한글 폰트 등록 성공: {font_path}")
                        break
                else:
                    print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
            except Exception as e:
                print(f"⚠️ 폰트 등록 실패: {e}")
    
    def _load_templates(self) -> Dict:
        """서류 템플릿 로딩"""
        return {
            # === 자유 양식 서류 ===
            "상업송장": {
                "form_type": FormType.FREE,
                "version": "2.0",
                "required_fields": [
                    "invoice_number", "issue_date", "exporter_name", "importer_name",
                    "product_name", "quantity", "unit_price", "total_amount"
                ],
                "optional_fields": [
                    "logo", "custom_header", "footer_text", "additional_terms"
                ],
                "layout_settings": {
                    "page_size": "A4",
                    "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
                    "header_height": 2,
                    "footer_height": 1
                },
                "styling": {
                    "title_font_size": 16,
                    "header_font_size": 12,
                    "body_font_size": 10,
                    "primary_color": "#2c3e50",
                    "secondary_color": "#3498db"
                }
            },
            
            "포장명세서": {
                "form_type": FormType.FREE,
                "version": "1.5",
                "required_fields": [
                    "packing_list_number", "issue_date", "exporter_name", "importer_name",
                    "product_details", "packing_details", "weight", "dimensions"
                ],
                "optional_fields": [
                    "logo", "custom_table_style", "additional_notes"
                ],
                "layout_settings": {
                    "page_size": "A4",
                    "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
                    "table_style": "grid"
                },
                "styling": {
                    "title_font_size": 14,
                    "header_font_size": 11,
                    "body_font_size": 9,
                    "table_header_color": "#ecf0f1"
                }
            },
            
            # === 규정 양식 서류 ===
            "원산지증명서": {
                "form_type": FormType.REGULATED,
                "version": "3.0",
                "required_fields": [
                    "certificate_number", "issue_date", "exporter_name", "importer_name",
                    "product_name", "origin_criteria", "manufacturing_process"
                ],
                "form_template": "certificate_of_origin_template.pdf",
                "field_mapping": {
                    "certificate_number": {"x": 100, "y": 700, "width": 200, "height": 20},
                    "issue_date": {"x": 100, "y": 650, "width": 150, "height": 20},
                    "exporter_name": {"x": 100, "y": 600, "width": 300, "height": 20},
                    "importer_name": {"x": 100, "y": 550, "width": 300, "height": 20},
                    "product_name": {"x": 100, "y": 500, "width": 300, "height": 20}
                },
                "styling": {
                    "font_size": 10,
                    "font_color": "#000000"
                }
            },
            
            "위생증명서": {
                "form_type": FormType.REGULATED,
                "version": "2.5",
                "required_fields": [
                    "health_certificate_number", "issue_date", "exporter_name",
                    "product_name", "health_standards", "inspection_results"
                ],
                "form_template": "health_certificate_template.pdf",
                "field_mapping": {
                    "health_certificate_number": {"x": 120, "y": 720, "width": 180, "height": 20},
                    "issue_date": {"x": 120, "y": 670, "width": 150, "height": 20},
                    "exporter_name": {"x": 120, "y": 620, "width": 280, "height": 20},
                    "product_name": {"x": 120, "y": 570, "width": 280, "height": 20}
                },
                "styling": {
                    "font_size": 10,
                    "font_color": "#000000"
                }
            },
            
            # === 혼합 양식 서류 ===
            "수출신고서": {
                "form_type": FormType.HYBRID,
                "version": "2.0",
                "required_fields": [
                    "declaration_number", "declaration_date", "exporter_name",
                    "product_name", "quantity", "value"
                ],
                "regulated_sections": ["header", "official_stamp_area"],
                "free_sections": ["additional_notes", "custom_fields"],
                "form_template": "export_declaration_template.pdf",
                "field_mapping": {
                    "declaration_number": {"x": 100, "y": 750, "width": 200, "height": 20},
                    "declaration_date": {"x": 100, "y": 700, "width": 150, "height": 20},
                    "exporter_name": {"x": 100, "y": 650, "width": 300, "height": 20}
                },
                "styling": {
                    "font_size": 10,
                    "font_color": "#000000",
                    "free_section_color": "#3498db"
                }
            }
        }
    
    def _load_form_templates(self) -> Dict:
        """규정 양식 PDF 템플릿 로딩"""
        return {
            "certificate_of_origin_template.pdf": {
                "path": "templates/forms/certificate_of_origin_template.pdf",
                "version": "3.0",
                "last_updated": "2024-01-15",
                "source": "관세청",
                "description": "원산지증명서 공식 양식"
            },
            "health_certificate_template.pdf": {
                "path": "templates/forms/health_certificate_template.pdf",
                "version": "2.5",
                "last_updated": "2024-01-10",
                "source": "식품의약품안전처",
                "description": "위생증명서 공식 양식"
            },
            "export_declaration_template.pdf": {
                "path": "templates/forms/export_declaration_template.pdf",
                "version": "2.0",
                "last_updated": "2024-01-20",
                "source": "관세청",
                "description": "수출신고서 공식 양식"
            }
        }
    
    def _load_customization_options(self) -> Dict:
        """사용자 커스터마이징 옵션"""
        return {
            "logo_options": {
                "position": ["top_left", "top_right", "top_center"],
                "size": ["small", "medium", "large"],
                "opacity": [0.5, 0.7, 0.9, 1.0]
            },
            "color_schemes": {
                "professional": {"primary": "#2c3e50", "secondary": "#3498db", "accent": "#e74c3c"},
                "modern": {"primary": "#34495e", "secondary": "#3498db", "accent": "#2ecc71"},
                "classic": {"primary": "#000000", "secondary": "#333333", "accent": "#666666"},
                "corporate": {"primary": "#1a237e", "secondary": "#3f51b5", "accent": "#7986cb"}
            },
            "font_options": {
                "korean": ["맑은 고딕", "굴림", "바탕"],
                "english": ["Arial", "Times New Roman", "Calibri"],
                "sizes": [8, 9, 10, 11, 12, 14, 16, 18]
            },
            "layout_options": {
                "page_size": ["A4", "Letter", "Legal"],
                "orientation": ["portrait", "landscape"],
                "margins": ["narrow", "normal", "wide"]
            }
        }
    
    def generate_pdf_document(self, doc_type: str, data: Dict, 
                            customization: Dict = None, output_path: str = None) -> str:
        """PDF 서류 생성"""
        
        # 서류 이름 정리 (괄호 제거)
        clean_doc_type = self._clean_document_name(doc_type)
        
        if clean_doc_type not in self.templates:
            raise ValueError(f"지원하지 않는 서류 유형: {doc_type} (정리된 이름: {clean_doc_type})")
        
        template = self.templates[clean_doc_type]
        form_type = template["form_type"]
        
        # 기본 커스터마이징 설정
        if customization is None:
            customization = self._get_default_customization()
        
        # 출력 파일 경로 설정
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"generated_documents/{doc_type}_{timestamp}.pdf"
        
        # 양식 유형에 따른 생성 방법 선택
        if form_type == FormType.FREE:
            return self._generate_free_form_pdf(clean_doc_type, data, customization, output_path)
        elif form_type == FormType.REGULATED:
            return self._generate_regulated_form_pdf(clean_doc_type, data, customization, output_path)
        elif form_type == FormType.HYBRID:
            return self._generate_hybrid_form_pdf(clean_doc_type, data, customization, output_path)
        else:
            raise ValueError(f"알 수 없는 양식 유형: {form_type}")
    
    def _clean_document_name(self, doc_type: str) -> str:
        """서류 이름에서 괄호와 영문 제거"""
        import re
        
        # 괄호와 그 안의 내용 제거
        clean_name = re.sub(r'\([^)]*\)', '', doc_type)
        
        # 앞뒤 공백 제거
        clean_name = clean_name.strip()
        
        # 서류 이름 매핑
        name_mapping = {
            "상업송장": "상업송장",
            "포장명세서": "포장명세서", 
            "원산지증명서": "원산지증명서",
            "선하증권": "선하증권",
            "수출신고필증": "수출신고필증",
            "위생증명서": "위생증명서",
            "수출신고서": "수출신고서"
        }
        
        return name_mapping.get(clean_name, clean_name)
    
    def _generate_free_form_pdf(self, doc_type: str, data: Dict, 
                               customization: Dict, output_path: str) -> str:
        """자유 양식 PDF 생성"""
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if not REPORTLAB_AVAILABLE:
            return self._generate_free_form_pdf_fpdf(doc_type, data, customization, output_path)
        
        try:
            # ReportLab을 사용한 고품질 PDF 생성
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 스타일 설정
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor(customization.get('primary_color', '#2c3e50'))
            )
            
            # 로고 추가
            if customization.get('logo_path') and os.path.exists(customization['logo_path']):
                logo = Image(customization['logo_path'], width=2*inch, height=1*inch)
                story.append(logo)
                story.append(Spacer(1, 20))
            
            # 제목
            title = Paragraph(f"{doc_type}", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 서류 내용 생성
            content = self._generate_document_content(doc_type, data, customization)
            story.extend(content)
            
            # PDF 생성
            doc.build(story)
            return output_path
            
        except Exception as e:
            print(f"❌ ReportLab PDF 생성 실패: {e}")
            # 실패 시 FPDF2로 대체
            return self._generate_free_form_pdf_fpdf(doc_type, data, customization, output_path)
    
    def _generate_free_form_pdf_fpdf(self, doc_type: str, data: Dict, 
                                    customization: Dict, output_path: str) -> str:
        """FPDF2를 사용한 자유 양식 PDF 생성"""
        
        if not FPDF_AVAILABLE:
            raise ImportError("PDF 생성 라이브러리가 설치되지 않았습니다.")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # 폰트 설정
            try:
                # 한국어 폰트 시도
                pdf.add_font('KoreanFont', '', 'C:/Windows/Fonts/malgun.ttf', uni=True)
                pdf.set_font('KoreanFont', '', 12)
            except:
                try:
                    # 기본 폰트 시도
                    pdf.set_font('Arial', '', 12)
                except:
                    # 최후 수단
                    pdf.set_font('Helvetica', '', 12)
            
            # 제목
            pdf.set_font_size(16)
            pdf.cell(0, 10, doc_type, ln=True, align='C')
            pdf.ln(10)
            
            # 서류 내용
            pdf.set_font_size(12)
            for key, value in data.items():
                if isinstance(value, dict):
                    pdf.cell(0, 10, f"{key}:", ln=True)
                    for sub_key, sub_value in value.items():
                        pdf.cell(0, 8, f"  {sub_key}: {sub_value}", ln=True)
                else:
                    pdf.cell(0, 10, f"{key}: {value}", ln=True)
            
            # PDF 저장
            pdf.output(output_path)
            return output_path
            
        except Exception as e:
            print(f"❌ FPDF2 PDF 생성 실패: {e}")
            # 최후 수단: 텍스트 파일 생성
            return self._generate_text_fallback(doc_type, data, output_path)
    
    def _generate_regulated_form_pdf(self, doc_type: str, data: Dict, 
                                    customization: Dict, output_path: str) -> str:
        """규정 양식 PDF 생성"""
        
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2가 설치되지 않았습니다.")
        
        template = self.templates[doc_type]
        form_template = template.get('form_template')
        
        if not form_template or form_template not in self.form_templates:
            raise ValueError(f"양식 템플릿을 찾을 수 없습니다: {form_template}")
        
        template_path = self.form_templates[form_template]['path']
        
        if not os.path.exists(template_path):
            # 템플릿이 없으면 기본 양식 생성
            return self._generate_default_regulated_form(doc_type, data, customization, output_path)
        
        # 기존 양식에 데이터 채우기
        return self._fill_pdf_form(template_path, data, template.get('field_mapping', {}), output_path)
    
    def _generate_hybrid_form_pdf(self, doc_type: str, data: Dict, 
                                 customization: Dict, output_path: str) -> str:
        """혼합 양식 PDF 생성"""
        
        template = self.templates[doc_type]
        regulated_sections = template.get('regulated_sections', [])
        free_sections = template.get('free_sections', [])
        
        # 규정 부분은 기존 양식 사용
        if template.get('form_template'):
            base_pdf = self._generate_regulated_form_pdf(doc_type, data, customization, output_path)
        else:
            base_pdf = self._generate_free_form_pdf(doc_type, data, customization, output_path)
        
        # 자유 부분 추가
        return self._add_free_sections_to_pdf(base_pdf, data, free_sections, customization)
    
    def _fill_pdf_form(self, template_path: str, data: Dict, 
                       field_mapping: Dict, output_path: str) -> str:
        """PDF 양식에 데이터 채우기"""
        
        try:
            with open(template_path, 'rb') as template_file:
                reader = PyPDF2.PdfReader(template_file)
                writer = PyPDF2.PdfWriter()
                
                # 첫 번째 페이지 가져오기
                page = reader.pages[0]
                
                # 데이터를 양식 필드에 채우기
                for field_name, field_info in field_mapping.items():
                    if field_name in data:
                        # 텍스트 필드에 데이터 삽입
                        page.merge_page(self._create_text_field(
                            data[field_name], 
                            field_info['x'], 
                            field_info['y'], 
                            field_info['width'], 
                            field_info['height']
                        ))
                
                writer.add_page(page)
                
                # PDF 저장
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return output_path
                
        except Exception as e:
            print(f"PDF 양식 채우기 실패: {e}")
            # 실패 시 기본 양식 생성
            return self._generate_default_regulated_form(doc_type, data, customization, output_path)
    
    def _generate_text_fallback(self, doc_type: str, data: Dict, output_path: str) -> str:
        """PDF 생성 실패 시 텍스트 파일로 대체"""
        try:
            # PDF 확장자를 txt로 변경
            text_path = output_path.replace('.pdf', '.txt')
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {doc_type} ===\n")
                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for key, value in data.items():
                    if isinstance(value, dict):
                        f.write(f"{key}:\n")
                        for sub_key, sub_value in value.items():
                            f.write(f"  {sub_key}: {sub_value}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            
            print(f"✅ 텍스트 파일 생성 완료: {text_path}")
            return text_path
            
        except Exception as e:
            print(f"❌ 텍스트 파일 생성도 실패: {e}")
            return output_path
    
    def _create_text_field(self, text: str, x: float, y: float, width: float, height: float):
        """텍스트 필드 생성"""
        
        if not REPORTLAB_AVAILABLE:
            return None
        
        # 임시 PDF에 텍스트 생성
        temp_pdf = f"temp_text_field_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        c = canvas.Canvas(temp_pdf, pagesize=(width, height))
        c.setFont("Helvetica", 10)
        c.drawString(0, height - 15, text)
        c.save()
        
        return temp_pdf
    
    def _generate_document_content(self, doc_type: str, data: Dict, 
                                  customization: Dict) -> List:
        """서류 내용 생성"""
        
        content = []
        styles = getSampleStyleSheet()
        
        # 기본 스타일
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=customization.get('font_size', 10),
            spaceAfter=6
        )
        
        # 데이터를 내용으로 변환
        for key, value in data.items():
            if isinstance(value, dict):
                # 테이블 형태로 표시
                table_data = [[key, str(value)]]
                table = Table(table_data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(table)
                content.append(Spacer(1, 12))
            else:
                # 일반 텍스트로 표시
                text = f"{key}: {value}"
                content.append(Paragraph(text, normal_style))
        
        return content
    
    def _get_default_customization(self) -> Dict:
        """기본 커스터마이징 설정"""
        return {
            'color_scheme': 'professional',
            'font_size': 10,
            'page_size': 'A4',
            'orientation': 'portrait',
            'margins': 'normal',
            'logo_position': 'top_left',
            'logo_size': 'medium'
        }
    
    def _generate_default_regulated_form(self, doc_type: str, data: Dict, 
                                        customization: Dict, output_path: str) -> str:
        """기본 규정 양식 생성"""
        
        # 규정 양식이 없을 때 기본 양식 생성
        return self._generate_free_form_pdf(doc_type, data, customization, output_path)
    
    def _add_free_sections_to_pdf(self, base_pdf: str, data: Dict, 
                                  free_sections: List, customization: Dict) -> str:
        """PDF에 자유 섹션 추가"""
        
        # 기존 PDF에 추가 페이지 생성
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(base_pdf, pagesize=A4)
            story = []
            
            # 자유 섹션 내용 추가
            for section in free_sections:
                if section in data:
                    story.append(Paragraph(f"{section}:", getSampleStyleSheet()['Heading2']))
                    story.append(Paragraph(str(data[section]), getSampleStyleSheet()['Normal']))
                    story.append(Spacer(1, 12))
            
            # PDF에 추가
            doc.build(story)
        
        return base_pdf
    
    def update_form_template(self, template_name: str, new_template_path: str, 
                           version: str = None) -> bool:
        """양식 템플릿 업데이트"""
        
        if not os.path.exists(new_template_path):
            return False
        
        # 템플릿 디렉토리 생성
        os.makedirs("templates/forms", exist_ok=True)
        
        # 새 템플릿 복사
        import shutil
        target_path = f"templates/forms/{template_name}"
        shutil.copy2(new_template_path, target_path)
        
        # 메타데이터 업데이트
        if template_name in self.form_templates:
            self.form_templates[template_name].update({
                'path': target_path,
                'version': version or self.form_templates[template_name]['version'],
                'last_updated': datetime.now().isoformat()
            })
        else:
            self.form_templates[template_name] = {
                'path': target_path,
                'version': version or '1.0',
                'last_updated': datetime.now().isoformat(),
                'source': '사용자 업로드',
                'description': f'{template_name} 사용자 정의 템플릿'
            }
        
        return True
    
    def get_template_info(self, doc_type: str) -> Dict:
        """템플릿 정보 조회"""
        
        if doc_type not in self.templates:
            return {"error": f"템플릿을 찾을 수 없습니다: {doc_type}"}
        
        template = self.templates[doc_type]
        info = {
            "name": doc_type,
            "form_type": template["form_type"].value,
            "version": template["version"],
            "required_fields": template["required_fields"],
            "optional_fields": template["optional_fields"],
            "customization_options": self._get_customization_options_for_doc(doc_type)
        }
        
        if template["form_type"] == FormType.REGULATED:
            form_template = template.get("form_template")
            if form_template and form_template in self.form_templates:
                info["form_template"] = self.form_templates[form_template]
        
        return info
    
    def _get_customization_options_for_doc(self, doc_type: str) -> Dict:
        """서류별 커스터마이징 옵션"""
        
        template = self.templates[doc_type]
        form_type = template["form_type"]
        
        options = {
            "color_schemes": self.customization_options["color_schemes"],
            "font_options": self.customization_options["font_options"],
            "layout_options": self.customization_options["layout_options"]
        }
        
        if form_type == FormType.FREE:
            options["logo_options"] = self.customization_options["logo_options"]
            options["layout_settings"] = template.get("layout_settings", {})
            options["styling"] = template.get("styling", {})
        
        return options

def main():
    """PDF 생성 시스템 테스트"""
    
    print("📄 고도화된 PDF 서류 생성 시스템")
    print("=" * 50)
    
    # PDF 생성기 초기화
    generator = AdvancedPDFGenerator()
    
    # 테스트 데이터
    test_data = {
        "invoice_number": "INV-2024-001",
        "issue_date": "2024-12-27",
        "exporter_name": "한국식품(주)",
        "importer_name": "중국식품수입(주)",
        "product_name": "한국 라면",
        "quantity": "1,000개",
        "unit_price": "USD 10.00",
        "total_amount": "USD 10,000.00"
    }
    
    # 커스터마이징 설정
    customization = {
        "color_scheme": "professional",
        "font_size": 11,
        "logo_position": "top_left",
        "page_size": "A4"
    }
    
    try:
        # 자유 양식 PDF 생성 (상업송장)
        print("\n🔧 자유 양식 PDF 생성 중...")
        invoice_pdf = generator.generate_pdf_document(
            "상업송장", test_data, customization
        )
        print(f"✅ 상업송장 PDF 생성 완료: {invoice_pdf}")
        
        # 규정 양식 PDF 생성 (원산지증명서)
        print("\n🔧 규정 양식 PDF 생성 중...")
        origin_pdf = generator.generate_pdf_document(
            "원산지증명서", test_data, customization
        )
        print(f"✅ 원산지증명서 PDF 생성 완료: {origin_pdf}")
        
        # 템플릿 정보 조회
        print("\n📋 템플릿 정보:")
        for doc_type in ["상업송장", "원산지증명서", "위생증명서"]:
            info = generator.get_template_info(doc_type)
            print(f"   📄 {doc_type}: {info['form_type']} 양식 (v{info['version']})")
        
        print(f"\n✅ PDF 생성 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ PDF 생성 실패: {e}")

if __name__ == "__main__":
    main() 