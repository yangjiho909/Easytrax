#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 통합 자동 서류 생성 시스템
- 상세화된 입력 정보 수집
- PDF 출력 기능 (자유/규정 양식)
- 템플릿 커스터마이징
- 다국어 지원
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# PDF 라이브러리들
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from PyPDF2 import PdfReader, PdfWriter
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF 라이브러리를 사용할 수 없습니다.")

@dataclass
class ProductInfo:
    """제품 상세 정보"""
    name: str
    hs_code: str
    description: str
    quantity: int
    unit: str
    unit_price: float
    total_amount: float
    origin: str
    weight: float
    volume: float

@dataclass
class ContractInfo:
    """계약 정보"""
    incoterms: str
    payment_terms: str
    currency: str
    contract_date: str
    delivery_date: str

@dataclass
class ShippingInfo:
    """운송 정보"""
    invoice_number: str
    invoice_date: str
    departure_port: str
    arrival_port: str
    transport_method: str
    vessel_name: str
    voyage_number: str
    shipping_date: str
    consignee: str
    notify_party: str

@dataclass
class PackagingInfo:
    """포장 정보"""
    package_type: str
    total_packages: int
    package_dimensions: str
    gross_weight: float
    net_weight: float
    marks_labels: str

@dataclass
class CompanyInfo:
    """회사 정보"""
    exporter_name: str
    exporter_address: str
    exporter_phone: str
    exporter_email: str
    importer_name: str
    importer_address: str
    importer_phone: str
    importer_email: str
    us_agent_name: str
    us_agent_contact: str

@dataclass
class SpecialInfo:
    """특수 정보"""
    production_date: str
    production_location: str
    inspection_results: str
    haccp_facility: str
    fsvp_info: str
    insurance_amount: float
    insurance_company: str
    signature_name: str
    signature_title: str

class EnhancedDocumentGenerator:
    """고도화된 서류 생성기"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.styles = self._load_styles()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _load_templates(self) -> Dict:
        """템플릿 로딩"""
        return {
            "commercial_invoice": {
                "type": "free",
                "name": "상업 송장",
                "required_fields": [
                    "product_info", "contract_info", "shipping_info", 
                    "company_info", "packaging_info"
                ],
                "templates": ["professional", "modern", "classic", "corporate"]
            },
            "packing_list": {
                "type": "free",
                "name": "포장 명세서",
                "required_fields": [
                    "product_info", "packaging_info", "shipping_info", 
                    "company_info"
                ],
                "templates": ["detailed", "compact", "professional"]
            },
            "certificate_of_origin": {
                "type": "regulated",
                "name": "원산지 증명서",
                "required_fields": [
                    "product_info", "company_info", "origin_info"
                ],
                "template_file": "templates/forms/certificate_of_origin.pdf"
            },
            "health_certificate": {
                "type": "regulated",
                "name": "검역 증명서",
                "required_fields": [
                    "product_info", "company_info", "special_info"
                ],
                "template_file": "templates/forms/health_certificate.pdf"
            },
            "export_declaration": {
                "type": "regulated",
                "name": "수출 신고서",
                "required_fields": [
                    "product_info", "contract_info", "shipping_info", 
                    "company_info"
                ],
                "template_file": "templates/forms/export_declaration.pdf"
            }
        }
    
    def _load_styles(self) -> Dict:
        """스타일 로딩"""
        return {
            "professional": {
                "font_family": "Helvetica",
                "font_size": 10,
                "primary_color": colors.darkblue,
                "secondary_color": colors.grey,
                "header_style": {
                    "fontSize": 16,
                    "fontName": "Helvetica-Bold",
                    "alignment": TA_CENTER,
                    "spaceAfter": 20
                }
            },
            "modern": {
                "font_family": "Arial",
                "font_size": 11,
                "primary_color": colors.darkgreen,
                "secondary_color": colors.lightgrey,
                "header_style": {
                    "fontSize": 18,
                    "fontName": "Arial-Bold",
                    "alignment": TA_LEFT,
                    "spaceAfter": 25
                }
            },
            "classic": {
                "font_family": "Times-Roman",
                "font_size": 12,
                "primary_color": colors.black,
                "secondary_color": colors.grey,
                "header_style": {
                    "fontSize": 14,
                    "fontName": "Times-Bold",
                    "alignment": TA_CENTER,
                    "spaceAfter": 15
                }
            },
            "corporate": {
                "font_family": "Helvetica",
                "font_size": 10,
                "primary_color": colors.darkred,
                "secondary_color": colors.lightgrey,
                "header_style": {
                    "fontSize": 16,
                    "fontName": "Helvetica-Bold",
                    "alignment": TA_CENTER,
                    "spaceAfter": 20
                }
            }
        }
    
    def collect_detailed_info(self) -> Dict:
        """상세화된 정보 수집"""
        info = {
            "product_info": self._collect_product_info(),
            "contract_info": self._collect_contract_info(),
            "shipping_info": self._collect_shipping_info(),
            "packaging_info": self._collect_packaging_info(),
            "company_info": self._collect_company_info(),
            "special_info": self._collect_special_info()
        }
        
        return info
    
    def _collect_product_info(self) -> Dict:
        """제품 정보 수집"""
        return {
            "name": "",
            "hs_code": "",
            "description": "",
            "quantity": 0,
            "unit": "",
            "unit_price": 0.0,
            "total_amount": 0.0,
            "origin": "",
            "weight": 0.0,
            "volume": 0.0
        }
    
    def _collect_contract_info(self) -> Dict:
        """계약 정보 수집"""
        return {
            "incoterms": "",
            "payment_terms": "",
            "currency": "USD",
            "contract_date": "",
            "delivery_date": ""
        }
    
    def _collect_shipping_info(self) -> Dict:
        """운송 정보 수집"""
        return {
            "invoice_number": "",
            "invoice_date": "",
            "departure_port": "",
            "arrival_port": "",
            "transport_method": "",
            "vessel_name": "",
            "voyage_number": "",
            "shipping_date": "",
            "consignee": "",
            "notify_party": ""
        }
    
    def _collect_packaging_info(self) -> Dict:
        """포장 정보 수집"""
        return {
            "package_type": "",
            "total_packages": 0,
            "package_dimensions": "",
            "gross_weight": 0.0,
            "net_weight": 0.0,
            "marks_labels": ""
        }
    
    def _collect_company_info(self) -> Dict:
        """회사 정보 수집"""
        return {
            "exporter_name": "",
            "exporter_address": "",
            "exporter_phone": "",
            "exporter_email": "",
            "importer_name": "",
            "importer_address": "",
            "importer_phone": "",
            "importer_email": "",
            "us_agent_name": "",
            "us_agent_contact": ""
        }
    
    def _collect_special_info(self) -> Dict:
        """특수 정보 수집"""
        return {
            "production_date": "",
            "production_location": "",
            "inspection_results": "",
            "haccp_facility": "",
            "fsvp_info": "",
            "insurance_amount": 0.0,
            "insurance_company": "",
            "signature_name": "",
            "signature_title": ""
        }
    
    def generate_document(self, doc_type: str, info: Dict, 
                         template_style: str = "professional",
                         customization: Dict = None) -> Dict:
        """서류 생성"""
        
        if doc_type not in self.templates:
            raise ValueError(f"지원하지 않는 서류 유형: {doc_type}")
        
        template_info = self.templates[doc_type]
        
        if template_info["type"] == "free":
            return self._generate_free_form_document(
                doc_type, info, template_style, customization
            )
        else:
            return self._generate_regulated_document(
                doc_type, info, template_info["template_file"]
            )
    
    def _generate_free_form_document(self, doc_type: str, info: Dict,
                                   template_style: str, customization: Dict) -> Dict:
        """자유 양식 서류 생성"""
        
        if not PDF_AVAILABLE:
            return self._generate_text_document(doc_type, info)
        
        # PDF 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_{timestamp}.pdf"
        filepath = os.path.join("generated_documents", filename)
        
        # 디렉토리 생성
        os.makedirs("generated_documents", exist_ok=True)
        
        # PDF 생성
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # 스타일 적용
        style = self.styles.get(template_style, self.styles["professional"])
        
        # 헤더 생성
        header_style = ParagraphStyle(
            "CustomHeader",
            parent=getSampleStyleSheet()["Heading1"],
            **style["header_style"]
        )
        
        story.append(Paragraph(self.templates[doc_type]["name"], header_style))
        story.append(Spacer(1, 20))
        
        # 로고 추가 (커스터마이징)
        if customization and customization.get("logo_path"):
            # 로고 이미지 추가 로직
            pass
        
        # 서류 내용 생성
        story.extend(self._create_document_content(doc_type, info, style))
        
        # 서명 섹션
        story.extend(self._create_signature_section(info, style))
        
        # PDF 빌드
        doc.build(story)
        
        return {
            "success": True,
            "file_path": filepath,
            "filename": filename,
            "document_type": doc_type,
            "template_style": template_style
        }
    
    def _generate_regulated_document(self, doc_type: str, info: Dict, 
                                   template_file: str) -> Dict:
        """규정 양식 서류 생성"""
        
        if not PDF_AVAILABLE:
            return self._generate_text_document(doc_type, info)
        
        # 템플릿 파일 확인
        if not os.path.exists(template_file):
            return {
                "success": False,
                "error": f"템플릿 파일을 찾을 수 없습니다: {template_file}"
            }
        
        # 출력 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_{timestamp}.pdf"
        output_path = os.path.join("generated_documents", filename)
        
        # 디렉토리 생성
        os.makedirs("generated_documents", exist_ok=True)
        
        try:
            # PDF 템플릿에 데이터 매핑
            self._fill_pdf_template(template_file, output_path, info)
            
            return {
                "success": True,
                "file_path": output_path,
                "filename": filename,
                "document_type": doc_type,
                "template_file": template_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF 생성 중 오류: {str(e)}"
            }
    
    def _fill_pdf_template(self, template_path: str, output_path: str, info: Dict):
        """PDF 템플릿에 데이터 채우기"""
        
        # PyPDF2를 사용한 템플릿 채우기
        reader = PdfReader(template_path)
        writer = PdfWriter()
        
        # 첫 번째 페이지 가져오기
        page = reader.pages[0]
        
        # 필드 매핑 정의
        field_mapping = self._get_field_mapping(info)
        
        # 필드 채우기
        for field_name, field_value in field_mapping.items():
            if field_name in page:
                page[field_name] = str(field_value)
        
        writer.add_page(page)
        
        # 출력 파일 저장
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
    
    def _get_field_mapping(self, info: Dict) -> Dict:
        """필드 매핑 생성"""
        mapping = {}
        
        # 제품 정보 매핑
        if "product_info" in info:
            product = info["product_info"]
            mapping.update({
                "product_name": product.get("name", ""),
                "hs_code": product.get("hs_code", ""),
                "quantity": product.get("quantity", ""),
                "unit_price": product.get("unit_price", ""),
                "total_amount": product.get("total_amount", ""),
                "origin": product.get("origin", "")
            })
        
        # 회사 정보 매핑
        if "company_info" in info:
            company = info["company_info"]
            mapping.update({
                "exporter_name": company.get("exporter_name", ""),
                "exporter_address": company.get("exporter_address", ""),
                "importer_name": company.get("importer_name", ""),
                "importer_address": company.get("importer_address", "")
            })
        
        # 계약 정보 매핑
        if "contract_info" in info:
            contract = info["contract_info"]
            mapping.update({
                "incoterms": contract.get("incoterms", ""),
                "payment_terms": contract.get("payment_terms", ""),
                "contract_date": contract.get("contract_date", "")
            })
        
        return mapping
    
    def _create_document_content(self, doc_type: str, info: Dict, style: Dict) -> List:
        """서류 내용 생성"""
        content = []
        
        if doc_type == "commercial_invoice":
            content.extend(self._create_commercial_invoice_content(info, style))
        elif doc_type == "packing_list":
            content.extend(self._create_packing_list_content(info, style))
        elif doc_type == "certificate_of_origin":
            content.extend(self._create_certificate_content(info, style))
        
        return content
    
    def _create_commercial_invoice_content(self, info: Dict, style: Dict) -> List:
        """상업 송장 내용 생성"""
        content = []
        
        # 회사 정보 테이블
        company_data = [
            ["수출자", info.get("company_info", {}).get("exporter_name", "")],
            ["수입자", info.get("company_info", {}).get("importer_name", "")],
            ["송장번호", info.get("shipping_info", {}).get("invoice_number", "")],
            ["송장일자", info.get("shipping_info", {}).get("invoice_date", "")]
        ]
        
        company_table = Table(company_data, colWidths=[2*inch, 4*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), style["primary_color"]),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), style["font_family"]),
            ('FONTSIZE', (0, 0), (-1, -1), style["font_size"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(company_table)
        content.append(Spacer(1, 20))
        
        # 제품 정보 테이블
        product_info = info.get("product_info", {})
        product_data = [
            ["품목", "HS코드", "수량", "단가", "총액", "원산지"],
            [
                product_info.get("name", ""),
                product_info.get("hs_code", ""),
                f"{product_info.get('quantity', '')} {product_info.get('unit', '')}",
                f"${product_info.get('unit_price', 0):,.2f}",
                f"${product_info.get('total_amount', 0):,.2f}",
                product_info.get("origin", "")
            ]
        ]
        
        product_table = Table(product_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), style["primary_color"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), style["font_family"]),
            ('FONTSIZE', (0, 0), (-1, -1), style["font_size"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(product_table)
        content.append(Spacer(1, 20))
        
        # 계약 조건
        contract_info = info.get("contract_info", {})
        contract_text = f"""
        <b>계약 조건:</b><br/>
        Incoterms: {contract_info.get('incoterms', '')}<br/>
        결제 조건: {contract_info.get('payment_terms', '')}<br/>
        통화: {contract_info.get('currency', 'USD')}
        """
        
        contract_para = Paragraph(contract_text, getSampleStyleSheet()["Normal"])
        content.append(contract_para)
        
        return content
    
    def _create_packing_list_content(self, info: Dict, style: Dict) -> List:
        """포장 명세서 내용 생성"""
        content = []
        
        # 포장 정보 테이블
        packaging_info = info.get("packaging_info", {})
        packing_data = [
            ["포장 유형", "총 개수", "총 중량", "총 부피", "마크/라벨"],
            [
                packaging_info.get("package_type", ""),
                packaging_info.get("total_packages", ""),
                f"{packaging_info.get('gross_weight', 0)} kg",
                f"{packaging_info.get('volume', 0)} CBM",
                packaging_info.get("marks_labels", "")
            ]
        ]
        
        packing_table = Table(packing_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])
        packing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), style["primary_color"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), style["font_family"]),
            ('FONTSIZE', (0, 0), (-1, -1), style["font_size"]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(packing_table)
        
        return content
    
    def _create_certificate_content(self, info: Dict, style: Dict) -> List:
        """증명서 내용 생성"""
        content = []
        
        # 기본 정보
        basic_info = info.get("product_info", {})
        basic_text = f"""
        <b>제품 정보:</b><br/>
        제품명: {basic_info.get('name', '')}<br/>
        HS코드: {basic_info.get('hs_code', '')}<br/>
        원산지: {basic_info.get('origin', '')}
        """
        
        basic_para = Paragraph(basic_text, getSampleStyleSheet()["Normal"])
        content.append(basic_para)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_signature_section(self, info: Dict, style: Dict) -> List:
        """서명 섹션 생성"""
        content = []
        
        special_info = info.get("special_info", {})
        signature_text = f"""
        <b>서명:</b><br/>
        이름: {special_info.get('signature_name', '')}<br/>
        직책: {special_info.get('signature_title', '')}<br/>
        날짜: {datetime.now().strftime('%Y년 %m월 %d일')}
        """
        
        signature_para = Paragraph(signature_text, getSampleStyleSheet()["Normal"])
        content.append(signature_para)
        
        return content
    
    def _generate_text_document(self, doc_type: str, info: Dict) -> Dict:
        """텍스트 기반 서류 생성 (PDF 불가능 시)"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_{timestamp}.txt"
        filepath = os.path.join("generated_documents", filename)
        
        os.makedirs("generated_documents", exist_ok=True)
        
        content = self._create_text_content(doc_type, info)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "file_path": filepath,
            "filename": filename,
            "document_type": doc_type,
            "format": "text"
        }
    
    def _create_text_content(self, doc_type: str, info: Dict) -> str:
        """텍스트 내용 생성"""
        content = []
        
        content.append(f"=== {self.templates[doc_type]['name']} ===")
        content.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # 제품 정보
        if "product_info" in info:
            product = info["product_info"]
            content.append("【제품 정보】")
            content.append(f"제품명: {product.get('name', '')}")
            content.append(f"HS코드: {product.get('hs_code', '')}")
            content.append(f"수량: {product.get('quantity', '')} {product.get('unit', '')}")
            content.append(f"단가: ${product.get('unit_price', 0):,.2f}")
            content.append(f"총액: ${product.get('total_amount', 0):,.2f}")
            content.append(f"원산지: {product.get('origin', '')}")
            content.append("")
        
        # 회사 정보
        if "company_info" in info:
            company = info["company_info"]
            content.append("【회사 정보】")
            content.append(f"수출자: {company.get('exporter_name', '')}")
            content.append(f"수출자 주소: {company.get('exporter_address', '')}")
            content.append(f"수입자: {company.get('importer_name', '')}")
            content.append(f"수입자 주소: {company.get('importer_address', '')}")
            content.append("")
        
        # 계약 정보
        if "contract_info" in info:
            contract = info["contract_info"]
            content.append("【계약 정보】")
            content.append(f"Incoterms: {contract.get('incoterms', '')}")
            content.append(f"결제 조건: {contract.get('payment_terms', '')}")
            content.append(f"통화: {contract.get('currency', 'USD')}")
            content.append("")
        
        return "\n".join(content)
    
    def get_template_info(self, doc_type: str) -> Dict:
        """템플릿 정보 조회"""
        if doc_type not in self.templates:
            return {"error": f"지원하지 않는 서류 유형: {doc_type}"}
        
        template = self.templates[doc_type]
        return {
            "type": template["type"],
            "name": template["name"],
            "required_fields": template["required_fields"],
            "available_templates": template.get("templates", []),
            "template_file": template.get("template_file", "")
        }
    
    def update_template(self, doc_type: str, template_file: str) -> Dict:
        """템플릿 업데이트"""
        if doc_type not in self.templates:
            return {"error": f"지원하지 않는 서류 유형: {doc_type}"}
        
        if not os.path.exists(template_file):
            return {"error": "템플릿 파일을 찾을 수 없습니다."}
        
        # 템플릿 파일 복사
        import shutil
        target_path = f"templates/forms/{doc_type}_template.pdf"
        os.makedirs("templates/forms", exist_ok=True)
        shutil.copy2(template_file, target_path)
        
        # 템플릿 정보 업데이트
        self.templates[doc_type]["template_file"] = target_path
        
        return {
            "success": True,
            "message": f"{doc_type} 템플릿이 업데이트되었습니다.",
            "template_file": target_path
        }

def main():
    """고도화된 서류 생성 시스템 테스트"""
    
    print("🚀 통합 자동 서류 생성 시스템")
    print("=" * 50)
    
    generator = EnhancedDocumentGenerator()
    
    # 사용 가능한 서류 유형 확인
    print("\n📋 지원하는 서류 유형:")
    for doc_type, info in generator.templates.items():
        print(f"   {info['name']} ({info['type']} 양식)")
    
    # 샘플 데이터 생성
    sample_info = {
        "product_info": {
            "name": "한국 라면",
            "hs_code": "1902.30.0000",
            "description": "인스턴트 라면",
            "quantity": 1000,
            "unit": "박스",
            "unit_price": 5.50,
            "total_amount": 5500.00,
            "origin": "대한민국",
            "weight": 500.0,
            "volume": 2.5
        },
        "contract_info": {
            "incoterms": "FOB",
            "payment_terms": "L/C at sight",
            "currency": "USD",
            "contract_date": "2024-12-01",
            "delivery_date": "2024-12-31"
        },
        "shipping_info": {
            "invoice_number": "INV-2024-001",
            "invoice_date": "2024-12-01",
            "departure_port": "부산항",
            "arrival_port": "로스앤젤레스항",
            "transport_method": "해상운송",
            "vessel_name": "EVER GIVEN",
            "voyage_number": "001W",
            "shipping_date": "2024-12-15",
            "consignee": "ABC Trading Co.",
            "notify_party": "ABC Trading Co."
        },
        "packaging_info": {
            "package_type": "카톤박스",
            "total_packages": 100,
            "package_dimensions": "40x30x20cm",
            "gross_weight": 500.0,
            "net_weight": 450.0,
            "marks_labels": "MADE IN KOREA"
        },
        "company_info": {
            "exporter_name": "한국식품(주)",
            "exporter_address": "서울시 강남구 테헤란로 123",
            "exporter_phone": "+82-2-1234-5678",
            "exporter_email": "export@koreafood.co.kr",
            "importer_name": "ABC Trading Co.",
            "importer_address": "123 Main St, Los Angeles, CA 90210",
            "importer_phone": "+1-213-555-0123",
            "importer_email": "import@abctrading.com",
            "us_agent_name": "US Agent LLC",
            "us_agent_contact": "+1-213-555-9999"
        },
        "special_info": {
            "production_date": "2024-11-15",
            "production_location": "경기도 안산시",
            "inspection_results": "합격",
            "haccp_facility": "HACCP 인증 시설",
            "fsvp_info": "FSVP 준수",
            "insurance_amount": 6000.00,
            "insurance_company": "한국해상보험",
            "signature_name": "김수출",
            "signature_title": "수출부장"
        }
    }
    
    # 상업 송장 생성 테스트
    print(f"\n📄 상업 송장 생성 테스트:")
    try:
        result = generator.generate_document(
            "commercial_invoice", 
            sample_info, 
            "professional",
            {"logo_path": "logo.png"}
        )
        
        if result["success"]:
            print(f"   ✅ 생성 성공: {result['filename']}")
            print(f"   📁 파일 경로: {result['file_path']}")
        else:
            print(f"   ❌ 생성 실패: {result.get('error', '알 수 없는 오류')}")
            
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
    
    # 템플릿 정보 조회
    print(f"\n📋 상업 송장 템플릿 정보:")
    template_info = generator.get_template_info("commercial_invoice")
    print(f"   유형: {template_info['type']}")
    print(f"   사용 가능한 템플릿: {', '.join(template_info['available_templates'])}")

if __name__ == "__main__":
    main() 