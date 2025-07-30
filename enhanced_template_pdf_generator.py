#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 개선된 템플릿 기반 PDF 서류 생성 시스템
- 더 간단하고 효과적인 템플릿 채우기
- 실제 양식 레이아웃 유지
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF

class EnhancedTemplatePDFGenerator:
    """개선된 템플릿 기반 PDF 생성기"""
    
    def __init__(self):
        self.template_dir = "uploaded_templates"
        self.templates = {
            "상업송장": "상업송장(Commercial Invoice).pdf",
            "포장명세서": "포장명세서(Packing List).pdf"
        }
        
        # 실제 템플릿에서 발견된 필드들의 정확한 텍스트
        self.template_fields = {
            "상업송장": {
                "송장번호": "8905  BK 1007 MAY. 20. 2007",
                "송장날짜": "MAY. 20. 2007",
                "판매자": "GILDING TRADING CO., LTD.",
                "판매자주소": "159, SAMSUNG-DONG, KANGNAM-KU,",
                "판매자국가": "SEOUL, KOREA",
                "판매자전화": "TEL: 82-2-1234-5678",
                "판매자이메일": "EMAIL: info@gilding.com",
                "구매자": "MONARCH PRO CO., LTD.",
                "구매자주소": "5200 ANTHONY WAVUE DR.",
                "구매자국가": "NEW YORK, NY 10001",
                "구매자전화": "TEL: 1-555-123-4567",
                "구매자이메일": "EMAIL: contact@monarch.com",
                "제품명": "description",
                "제품코드": "HS Code",
                "수량": "⑮Quantity",
                "단위": "Unit",
                "단가": "Unit price",
                "총액": "Amount",
                "원산지": "Country of Origin",
                "출발항": "Port of Loading",
                "도착항": "Port of Discharge",
                "운송방식": "Terms of Delivery",
                "L/C번호": "55352 APR. 25. 2007"
            },
            "포장명세서": {
                "포장번호": "Package No",
                "송장번호": "Invoice No",
                "송장날짜": "Invoice Date",
                "판매자": "Shipper",
                "구매자": "Consignee",
                "제품명": "Description",
                "제품코드": "HS Code",
                "수량": "Quantity",
                "단위": "Unit",
                "무게": "Weight",
                "부피": "Volume",
                "포장타입": "Package Type",
                "총포장수": "Total Packages",
                "총무게": "Total Weight",
                "총부피": "Total Volume",
                "원산지": "Country of Origin",
                "출발항": "Port of Loading",
                "도착항": "Port of Discharge",
                "운송방식": "Terms of Delivery"
            }
        }
    
    def generate_filled_pdf(self, doc_type: str, data: Dict, output_path: str) -> str:
        """템플릿에 데이터를 채워 PDF 생성"""
        try:
            print(f"📄 {doc_type} 템플릿 기반 PDF 생성 시작")
            
            # 템플릿 파일 경로
            template_path = os.path.join(self.template_dir, self.templates[doc_type])
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
            
            # 템플릿 복사
            doc = fitz.open(template_path)
            
            # 데이터 매핑
            mapped_data = self._map_data_to_template(doc_type, data)
            print(f"📋 매핑된 데이터: {mapped_data}")
            
            # 템플릿 채우기
            success = self._fill_template_simple(doc, doc_type, mapped_data)
            
            # PDF 저장
            doc.save(output_path)
            doc.close()
            
            if success:
                print(f"✅ 템플릿 기반 PDF 생성 완료: {output_path}")
                return output_path
            else:
                print(f"⚠️ 템플릿 채우기 실패, 폴백 사용")
                return self._generate_fallback_pdf(doc_type, data, output_path)
            
        except Exception as e:
            print(f"❌ 템플릿 기반 PDF 생성 실패: {e}")
            return self._generate_fallback_pdf(doc_type, data, output_path)
    
    def _fill_template_simple(self, doc, doc_type: str, mapped_data: Dict) -> bool:
        """간단한 템플릿 채우기 방법"""
        try:
            success_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 페이지의 모든 텍스트 블록 가져오기
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                
                                # 매핑된 데이터와 매칭
                                for field_name, new_value in mapped_data.items():
                                    if field_name in self.template_fields[doc_type]:
                                        original_text = self.template_fields[doc_type][field_name]
                                        
                                        # 텍스트 매칭 (부분 매칭도 허용)
                                        if original_text.lower() in text.lower() or text.lower() in original_text.lower():
                                            try:
                                                # 기존 텍스트 영역 지우기
                                                bbox = span["bbox"]
                                                page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
                                                
                                                # 새 텍스트 삽입
                                                font_size = span.get("size", 12)
                                                page.insert_text(
                                                    point=(bbox[0], bbox[1] + font_size),
                                                    text=new_value,
                                                    fontsize=font_size
                                                )
                                                
                                                success_count += 1
                                                print(f"✅ 필드 교체 성공: {field_name} -> {new_value}")
                                                break
                                                
                                            except Exception as e:
                                                print(f"⚠️ 필드 교체 실패: {field_name} - {e}")
                                                continue
            
            print(f"📊 템플릿 채우기 결과: {success_count}/{len(mapped_data)} 필드 성공")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 템플릿 채우기 오류: {e}")
            return False
    
    def _map_data_to_template(self, doc_type: str, data: Dict) -> Dict:
        """사용자 데이터를 템플릿 필드에 매핑"""
        mapped_data = {}
        
        # 공통 필드
        timestamp = datetime.now()
        invoice_number = f"INV-{timestamp.strftime('%Y%m%d%H%M%S')}"
        package_number = f"PKG-{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        # 데이터 추출
        company_info = data.get('company_info', {})
        buyer_info = data.get('buyer_info', {})
        product_info = data.get('product_info', {})
        transport_info = data.get('transport_info', {})
        
        if doc_type == "상업송장":
            mapped_data = {
                "송장번호": invoice_number,
                "송장날짜": timestamp.strftime('%Y-%m-%d'),
                "판매자": company_info.get('name', ''),
                "판매자주소": company_info.get('address', ''),
                "판매자국가": "SEOUL, KOREA",
                "판매자전화": f"TEL: {company_info.get('phone', '')}",
                "판매자이메일": f"EMAIL: {company_info.get('email', '')}",
                "구매자": buyer_info.get('name', ''),
                "구매자주소": buyer_info.get('address', ''),
                "구매자국가": f"{buyer_info.get('address', '').split(',')[-1].strip() if buyer_info.get('address') else ''}",
                "구매자전화": f"TEL: {buyer_info.get('phone', '')}",
                "구매자이메일": f"EMAIL: {buyer_info.get('email', '')}",
                "제품명": product_info.get('name', ''),
                "제품코드": product_info.get('code', ''),
                "수량": str(product_info.get('quantity', 0)),
                "단위": product_info.get('unit', '개'),
                "단가": f"${product_info.get('unit_price', 0)}",
                "총액": f"${product_info.get('quantity', 0) * product_info.get('unit_price', 0)}",
                "원산지": product_info.get('origin', 'KOREA'),
                "출발항": transport_info.get('port_of_departure', 'BUSAN, KOREA'),
                "도착항": transport_info.get('port_of_arrival', ''),
                "운송방식": transport_info.get('mode', 'SEA'),
                "L/C번호": f"LC-{timestamp.strftime('%Y%m%d')}"
            }
        elif doc_type == "포장명세서":
            mapped_data = {
                "포장번호": package_number,
                "송장번호": invoice_number,
                "송장날짜": timestamp.strftime('%Y-%m-%d'),
                "판매자": company_info.get('name', ''),
                "구매자": buyer_info.get('name', ''),
                "제품명": product_info.get('name', ''),
                "제품코드": product_info.get('code', ''),
                "수량": str(product_info.get('quantity', 0)),
                "단위": product_info.get('unit', '개'),
                "무게": f"{product_info.get('weight', 0)}kg",
                "부피": f"{product_info.get('volume', 0)}m³",
                "포장타입": transport_info.get('package_type', 'Carton'),
                "총포장수": "1",
                "총무게": f"{product_info.get('weight', 0)}kg",
                "총부피": f"{product_info.get('volume', 0)}m³",
                "원산지": product_info.get('origin', 'KOREA'),
                "출발항": transport_info.get('port_of_departure', 'BUSAN, KOREA'),
                "도착항": transport_info.get('port_of_arrival', ''),
                "운송방식": transport_info.get('mode', 'SEA')
            }
        
        return mapped_data
    
    def _generate_fallback_pdf(self, doc_type: str, data: Dict, output_path: str) -> str:
        """폴백: 기본 PDF 생성"""
        try:
            from simple_pdf_generator import SimplePDFGenerator
            pdf_generator = SimplePDFGenerator()
            return pdf_generator.generate_pdf(doc_type, data, output_path)
        except Exception as e:
            print(f"❌ 폴백 PDF 생성도 실패: {e}")
            return output_path
    
    def get_template_info(self, doc_type: str) -> Dict:
        """템플릿 정보 반환"""
        try:
            template_path = os.path.join(self.template_dir, self.templates[doc_type])
            if os.path.exists(template_path):
                doc = fitz.open(template_path)
                info = {
                    "doc_type": doc_type,
                    "template_path": template_path,
                    "pages": len(doc),
                    "fields": self.template_fields.get(doc_type, {})
                }
                doc.close()
                return info
            else:
                return {"error": f"템플릿 파일을 찾을 수 없습니다: {template_path}"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_available_templates(self) -> List[str]:
        """사용 가능한 템플릿 목록"""
        return list(self.templates.keys())

# 전역 인스턴스
enhanced_template_pdf_generator = EnhancedTemplatePDFGenerator() 