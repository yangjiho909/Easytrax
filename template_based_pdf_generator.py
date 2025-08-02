#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 템플릿 기반 PDF 서류 생성 시스템
- uploaded_templates 폴더의 PDF 템플릿 분석
- 사용자 데이터를 템플릿에 맞춰 채우기
- 원본 레이아웃 유지
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF

class TemplateBasedPDFGenerator:
    """템플릿 기반 PDF 생성기"""
    
    def __init__(self):
        self.template_dir = "uploaded_templates"
        self.templates = {
            "상업송장": "상업송장(Commercial Invoice).pdf",
            "포장명세서": "포장명세서(Packing List).pdf"
        }
        self.field_patterns = {
            "상업송장": {
                "송장번호": r"Invoice No\.|송장번호|INVOICE NO",
                "송장날짜": r"date|날짜|DATE",
                "판매자": r"Shipper/Seller|판매자|SELLER",
                "구매자": r"Consignee|구매자|BUYER",
                "제품명": r"Description|제품명|상품명",
                "수량": r"Quantity|수량|QTY",
                "단가": r"Unit Price|단가|PRICE",
                "총액": r"Amount|총액|TOTAL",
                "회사명": r"CO\.|LTD\.|회사|COMPANY",
                "주소": r"ADDRESS|주소|ADDR",
                "전화번호": r"TEL|PHONE|전화",
                "이메일": r"EMAIL|이메일|E-MAIL"
            },
            "포장명세서": {
                "포장번호": r"Package No|포장번호|PKG NO",
                "제품명": r"Description|제품명|상품명",
                "수량": r"Quantity|수량|QTY",
                "무게": r"Weight|무게|WT",
                "포장타입": r"Package Type|포장타입|PKG TYPE",
                "총포장수": r"Total Packages|총포장수|TOTAL PKGS"
            }
        }
    
    def analyze_template(self, doc_type: str) -> Dict:
        """템플릿 분석"""
        if doc_type not in self.templates:
            raise ValueError(f"지원하지 않는 서류 유형: {doc_type}")
        
        template_path = os.path.join(self.template_dir, self.templates[doc_type])
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        
        try:
            doc = fitz.open(template_path)
            template_info = {
                "doc_type": doc_type,
                "template_path": template_path,
                "pages": len(doc),
                "fields": {},
                "text_content": ""
            }
            
            # 텍스트 내용 추출
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                template_info["text_content"] += text
                
                # 필드 위치 분석
                fields = self._analyze_fields_on_page(page, doc_type, page_num)
                template_info["fields"].update(fields)
            
            doc.close()
            return template_info
            
        except Exception as e:
            print(f"❌ 템플릿 분석 실패: {e}")
            raise
    
    def _analyze_fields_on_page(self, page, doc_type: str, page_num: int) -> Dict:
        """페이지에서 필드 위치 분석"""
        fields = {}
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        
                        # 필드 패턴 매칭
                        for field_name, pattern in self.field_patterns[doc_type].items():
                            if re.search(pattern, text, re.IGNORECASE):
                                bbox = span["bbox"]
                                fields[field_name] = {
                                    "text": text,
                                    "bbox": bbox,
                                    "page": page_num,
                                    "font_size": span.get("size", 12),
                                    "font_name": span.get("font", "Arial")
                                }
                                break
        
        return fields
    
    def generate_filled_pdf(self, doc_type: str, data: Dict, output_path: str) -> str:
        """템플릿에 데이터를 채워 PDF 생성"""
        try:
            # 템플릿 분석
            template_info = self.analyze_template(doc_type)
            
            # 템플릿 복사
            doc = fitz.open(template_info["template_path"])
            
            # 데이터 매핑 및 채우기
            success = self._fill_template_data(doc, template_info, data)
            
            # PDF 저장
            doc.save(output_path)
            doc.close()
            
            if success:
                print(f"✅ 템플릿 기반 PDF 생성 완료: {output_path}")
                return output_path
            else:
                print(f"⚠️ 템플릿 기반 PDF 생성 부분 실패, 폴백 사용: {output_path}")
                return self._generate_fallback_pdf(doc_type, data, output_path)
            
        except Exception as e:
            print(f"❌ 템플릿 기반 PDF 생성 실패: {e}")
            # 폴백: 기본 PDF 생성
            return self._generate_fallback_pdf(doc_type, data, output_path)
    
    def _fill_template_data(self, doc, template_info: Dict, data: Dict) -> bool:
        """템플릿에 데이터 채우기"""
        doc_type = template_info["doc_type"]
        
        # 데이터 매핑
        mapped_data = self._map_data_to_template(doc_type, data)
        
        success_count = 0
        total_fields = len(mapped_data)
        
        # 각 페이지에서 데이터 채우기
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 기존 텍스트 블록 찾기 및 교체
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            
                            # 매핑된 데이터로 교체
                            for field_name, new_value in mapped_data.items():
                                if field_name in template_info["fields"]:
                                    field_info = template_info["fields"][field_name]
                                    if field_info["text"] == text:
                                        # 텍스트 교체
                                        try:
                                            self._replace_text_on_page(page, span, new_value)
                                            success_count += 1
                                            print(f"✅ 필드 교체 성공: {field_name} -> {new_value}")
                                        except Exception as e:
                                            print(f"⚠️ 필드 교체 실패: {field_name} - {e}")
                                        break
        
        print(f"📊 템플릿 채우기 결과: {success_count}/{total_fields} 필드 성공")
        return success_count > 0  # 최소 1개 필드라도 성공하면 True
    
    def _map_data_to_template(self, doc_type: str, data: Dict) -> Dict:
        """사용자 데이터를 템플릿 필드에 매핑"""
        mapped_data = {}
        
        if doc_type == "상업송장":
            # 송장 정보
            mapped_data["송장번호"] = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            mapped_data["송장날짜"] = datetime.now().strftime("%Y-%m-%d")
            
            # 회사 정보
            company_info = data.get("company_info", {})
            mapped_data["판매자"] = company_info.get("name", "한국기업")
            mapped_data["회사명"] = company_info.get("name", "한국기업")
            
            # 제품 정보
            product_info = data.get("product_info", {})
            mapped_data["제품명"] = product_info.get("name", "제품")
            mapped_data["수량"] = str(product_info.get("quantity", 0))
            mapped_data["단가"] = f"${product_info.get("unit_price", 0)}"
            mapped_data["총액"] = f"${product_info.get("quantity", 0) * product_info.get("unit_price", 0)}"
            
        elif doc_type == "포장명세서":
            # 포장 정보
            mapped_data["포장번호"] = f"PKG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 제품 정보
            product_info = data.get("product_info", {})
            mapped_data["제품명"] = product_info.get("name", "제품")
            mapped_data["수량"] = str(product_info.get("quantity", 0))
            mapped_data["무게"] = f"{product_info.get('weight', 0)}kg"
            mapped_data["포장타입"] = "Carton"
            mapped_data["총포장수"] = "1"
        
        return mapped_data
    
    def _replace_text_on_page(self, page, span: Dict, new_text: str):
        """페이지에서 텍스트 교체"""
        try:
            # 기존 텍스트 영역 지우기
            bbox = span["bbox"]
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
            
            # 새 텍스트 삽입
            font_size = span.get("size", 12)
            
            # 폰트 문제 해결: 기본 폰트 사용
            try:
                page.insert_text(
                    point=(bbox[0], bbox[1] + font_size),
                    text=new_text,
                    fontsize=font_size,
                    fontname="helv"  # 기본 Helvetica 폰트 사용
                )
            except:
                # 폰트 실패 시 더 간단한 방법 사용
                page.insert_text(
                    point=(bbox[0], bbox[1] + font_size),
                    text=new_text,
                    fontsize=font_size
                )
            
        except Exception as e:
            print(f"⚠️ 텍스트 교체 실패: {e}")
            # 텍스트 교체 실패 시에도 계속 진행
    
    def _generate_fallback_pdf(self, doc_type: str, data: Dict, output_path: str) -> str:
        """폴백: 기본 PDF 생성"""
        try:
            from simple_pdf_generator import SimplePDFGenerator
            pdf_generator = SimplePDFGenerator()
            
            # 데이터를 텍스트로 변환
            content = f"=== {doc_type} ===\n\n"
            for key, value in data.items():
                content += f"{key}: {value}\n"
            
            success = pdf_generator.generate_pdf(content, output_path, doc_type)
            if success:
                return output_path
            else:
                # 텍스트 파일로 대체
                txt_path = output_path.replace('.pdf', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return txt_path
                
        except Exception as e:
            print(f"❌ 폴백 PDF 생성도 실패: {e}")
            # 텍스트 파일로 대체
            txt_path = output_path.replace('.pdf', '.txt')
            content = f"=== {doc_type} ===\n\n"
            for key, value in data.items():
                content += f"{key}: {value}\n"
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return txt_path
    
    def get_template_info(self, doc_type: str) -> Dict:
        """템플릿 정보 반환"""
        try:
            return self.analyze_template(doc_type)
        except Exception as e:
            return {"error": str(e)}
    
    def list_available_templates(self) -> List[str]:
        """사용 가능한 템플릿 목록"""
        return list(self.templates.keys())

# 전역 인스턴스
template_pdf_generator = TemplateBasedPDFGenerator() 