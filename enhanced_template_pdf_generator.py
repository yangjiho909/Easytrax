#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
향상된 템플릿 PDF 생성기
새로운 빈 템플릿을 사용하여 PDF 생성
"""

import fitz  # PyMuPDF
import os
from datetime import datetime
from typing import Dict, Any

class EnhancedTemplatePDFGenerator:
    def __init__(self):
        self.template_dir = "uploaded_templates"
        
        # 새로운 빈 템플릿 파일 경로
        self.template_files = {
            "상업송장": "상업송장 빈 템플릿.pdf",
            "포장명세서": "포장명세서 빈템플릿.pdf"
        }
    
    def map_data_to_new_templates(self, doc_type: str, data: Dict[str, Any]) -> Dict[str, str]:
        """새로운 템플릿에 데이터 매핑 - 영어 필드명 사용"""
        timestamp = datetime.now()
        invoice_number = f"INV-{timestamp.strftime('%Y%m%d%H%M%S')}"
        package_number = f"PKG-{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        company_info = data.get('company_info', {})
        buyer_info = data.get('buyer_info', {})
        product_info = data.get('product_info', {})
        transport_info = data.get('transport_info', {})
        payment_info = data.get('payment_info', {})
        packing_details = data.get('packing_details', {})
        
        if doc_type == "상업송장":
            return {
                # 정확한 필드명으로 매핑 (기존 템플릿 분석 결과 기반)
                "Invoice No. and date": f"{invoice_number} {timestamp.strftime('%Y-%m-%d')}",
                "L/C No. and date": f"LC-{timestamp.strftime('%Y%m%d')} {timestamp.strftime('%Y-%m-%d')}",
                "Shipper/Seller": company_info.get('name', ''),
                "Consignee": buyer_info.get('name', ''),
                "Buyer(if other than consignee)": buyer_info.get('name', ''),
                "Departure date": timestamp.strftime('%Y-%m-%d'),
                "Vessel/flight": transport_info.get('vessel_name', ''),
                "From": transport_info.get('port_of_departure', ''),
                "To": transport_info.get('port_of_arrival', ''),
                "Terms of delivery and payment": f"{transport_info.get('mode', '')} {payment_info.get('method', '')}",
                "Shipping Marks": packing_details.get('marks', ''),
                "No.&kind of": str(packing_details.get('total_packages', 0)),  # 정확한 필드명
                "packages": str(packing_details.get('total_packages', 0)),  # 정확한 필드명
                "Goods": product_info.get('name', ''),  # 정확한 필드명
                "description": product_info.get('name', ''),  # 정확한 필드명
                "Quantity": str(product_info.get('quantity', 0)),
                "Unit price": f"${product_info.get('unit_price', 0)}",
                "Amount": f"${product_info.get('quantity', 0) * product_info.get('unit_price', 0)}"
            }
        
        elif doc_type == "포장명세서":
            return {
                # 정확한 필드명으로 매핑 (기존 템플릿 분석 결과 기반)
                "Invoice No. and date": f"{invoice_number} {timestamp.strftime('%Y-%m-%d')}",
                "Seller": company_info.get('name', ''),
                "Consignee": buyer_info.get('name', ''),
                "Buyer(if other than consignee)": buyer_info.get('name', ''),
                "Departure date": timestamp.strftime('%Y-%m-%d'),
                "Vessel/flight": transport_info.get('vessel_name', ''),
                "From": transport_info.get('port_of_departure', ''),
                "To": transport_info.get('port_of_arrival', ''),
                "Shipping Marks": packing_details.get('marks', ''),
                "No.&kind of": str(packing_details.get('total_packages', 0)),  # 정확한 필드명
                "packages": str(packing_details.get('total_packages', 0)),  # 정확한 필드명
                "Goods": product_info.get('name', ''),  # 정확한 필드명
                "description": product_info.get('name', ''),  # 정확한 필드명
                "Quantity": str(product_info.get('quantity', 0)),  # 정확한 필드명
                "or net": str(product_info.get('quantity', 0)),  # 정확한 필드명
                "weight": str(product_info.get('quantity', 0)),  # 정확한 필드명
                "Gross": f"{packing_details.get('total_weight', 0)} kg",  # 정확한 필드명
                "Weight": f"{packing_details.get('total_weight', 0)} kg",  # 정확한 필드명
                "Measurement": f"{packing_details.get('total_volume', 0)} m³"
            }
        
        return {}
    
    def find_text_positions(self, doc, search_texts):
        """PDF에서 텍스트 위치 찾기"""
        positions = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.get_text("dict")
            
            for block in text_instances["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            for search_text in search_texts:
                                if search_text in text:
                                    # 텍스트 위치 정보 저장
                                    rect = span["bbox"]
                                    positions[search_text] = {
                                        'page': page_num,
                                        'rect': rect,
                                        'text': text,
                                        'font_size': span.get('size', 12)
                                    }
        
        return positions
    
    def fill_template_with_data(self, template_path: str, mapped_data: Dict[str, str], output_path: str):
        """템플릿에 데이터 채우기 - 텍스트 박스 위치에 실제 데이터 삽입"""
        try:
            # 템플릿 PDF 열기
            doc = fitz.open(template_path)
            
            # 텍스트 박스와 실제 데이터 매핑
            text_box_mapping = {
                # 상업송장 매핑
                "[송장번호]": "Invoice No. and date",
                "[L/C번호]": "L/C No. and date", 
                "[판매자]": "Shipper/Seller",
                "[구매자]": "Consignee",
                "[구매자명]": "Buyer(if other than consignee)",
                "[출발일]": "Departure date",
                "[선박명]": "Vessel/flight",
                "[출발지]": "From",
                "[도착지]": "To",
                "[결제조건]": "Terms of delivery and payment",
                "[선적마크]": "Shipping Marks",
                "[포장수량]": "No.&kind of",
                "[제품명]": "Goods",
                "[수량]": "Quantity",
                "[단가]": "Unit price",
                "[총액]": "Amount",
                
                # 포장명세서 매핑
                "[수하인]": "Consignee",
                "[통지처]": "Notify Party",
                "[기타참조]": "Other references",
                "[총무게]": "Gross",
                "[총부피]": "Measurement",
                "[서명자]": "Signed by"
            }
            
            # 각 텍스트 박스를 찾아서 실제 데이터로 교체
            for text_box, data_field in text_box_mapping.items():
                if data_field in mapped_data:
                    field_value = mapped_data[data_field]
                    if not field_value:  # 빈 값은 건너뛰기
                        continue
                    
                    # 텍스트 박스 위치 찾기
                    positions = self.find_text_positions(doc, [text_box])
                    
                    if text_box in positions:
                        pos = positions[text_box]
                        page = doc[pos['page']]
                        rect = pos['rect']
                        
                        # 기존 텍스트 박스 지우기 (빨간색으로 덮어쓰기)
                        page.add_redact_annot(rect, fill=(1, 1, 1))  # 흰색으로 덮어쓰기
                        page.apply_redactions()
                        
                        # 실제 데이터 삽입 (기존 텍스트 박스 위치에)
                        page.insert_text(
                            point=(rect[0], rect[1] + (rect[3] - rect[1]) / 2),  # 텍스트 박스 중앙
                            text=field_value,
                            fontsize=pos['font_size'],
                            color=(0, 0, 0)  # 검은색
                        )
                        print(f"✅ {text_box} → {field_value} 삽입 완료")
                    else:
                        print(f"⚠️ 텍스트 박스를 찾을 수 없음: {text_box}")
            
            # 결과 저장
            doc.save(output_path)
            doc.close()
            
            print(f"✅ PDF 생성 완료: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ PDF 생성 오류: {str(e)}")
            return False
    
    def generate_filled_pdf(self, doc_type: str, data: Dict[str, Any], output_path: str):
        """완성된 PDF 생성"""
        try:
            # 템플릿 파일 경로 확인
            template_filename = self.template_files.get(doc_type)
            if not template_filename:
                print(f"❌ 템플릿 파일을 찾을 수 없음: {doc_type}")
                return False
            
            template_path = os.path.join(self.template_dir, template_filename)
            if not os.path.exists(template_path):
                print(f"❌ 템플릿 파일이 존재하지 않음: {template_path}")
                return False
            
            # 데이터 매핑
            mapped_data = self.map_data_to_new_templates(doc_type, data)
            print(f"📝 매핑된 데이터: {mapped_data}")
            
            # PDF 생성
            success = self.fill_template_with_data(template_path, mapped_data, output_path)
            
            if success:
                print(f"🎉 {doc_type} PDF 생성 성공!")
                return True
            else:
                print(f"❌ {doc_type} PDF 생성 실패!")
                return False
                
        except Exception as e:
            print(f"❌ PDF 생성 중 오류: {str(e)}")
            return False

# 전역 인스턴스 생성
enhanced_template_pdf_generator = EnhancedTemplatePDFGenerator()

def generate_filled_pdf(doc_type: str, data: Dict[str, Any], output_path: str):
    """외부에서 호출할 함수"""
    return enhanced_template_pdf_generator.generate_filled_pdf(doc_type, data, output_path) 