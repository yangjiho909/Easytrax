#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 실제 템플릿 분석 - 모든 필드 찾기
"""

import os
import fitz  # PyMuPDF

def analyze_template_fields():
    """실제 템플릿에서 모든 필드 분석"""
    
    templates = {
        "상업송장": "uploaded_templates/상업송장(Commercial Invoice).pdf",
        "포장명세서": "uploaded_templates/포장명세서(Packing List).pdf"
    }
    
    for doc_type, template_path in templates.items():
        print(f"\n📄 {doc_type} 템플릿 분석")
        print("=" * 50)
        
        if not os.path.exists(template_path):
            print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
            continue
        
        try:
            doc = fitz.open(template_path)
            print(f"📋 페이지 수: {len(doc)}")
            
            all_fields = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                print(f"\n📄 페이지 {page_num + 1} 분석:")
                
                # 페이지의 모든 텍스트 블록 가져오기
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text and len(text) > 2:  # 의미있는 텍스트만
                                    bbox = span["bbox"]
                                    font_size = span.get("size", 12)
                                    font_name = span.get("font", "Unknown")
                                    
                                    field_info = {
                                        "text": text,
                                        "bbox": bbox,
                                        "page": page_num,
                                        "font_size": font_size,
                                        "font_name": font_name
                                    }
                                    all_fields.append(field_info)
                                    
                                    print(f"  - '{text}' (폰트: {font_name}, 크기: {font_size})")
            
            doc.close()
            
            print(f"\n📊 {doc_type} 총 필드 수: {len(all_fields)}")
            
            # 중요한 필드들 분류
            important_fields = []
            for field in all_fields:
                text = field["text"].lower()
                
                # 상업송장 관련 키워드
                if doc_type == "상업송장":
                    keywords = [
                        "invoice", "송장", "date", "날짜", "shipper", "seller", "판매자", 
                        "consignee", "buyer", "구매자", "description", "제품명", "상품명",
                        "quantity", "수량", "qty", "unit", "price", "단가", "amount", "총액",
                        "total", "address", "주소", "phone", "tel", "전화", "email", "이메일",
                        "company", "회사", "ltd", "co", "inc", "corp", "port", "항구", "country", "국가"
                    ]
                else:  # 포장명세서
                    keywords = [
                        "packing", "포장", "list", "명세서", "package", "no", "번호",
                        "description", "제품명", "상품명", "quantity", "수량", "qty",
                        "weight", "무게", "wt", "kg", "lb", "type", "타입", "total", "총",
                        "dimension", "크기", "size", "measurement", "측정", "volume", "부피"
                    ]
                
                for keyword in keywords:
                    if keyword in text:
                        important_fields.append(field)
                        break
            
            print(f"\n🎯 {doc_type} 중요 필드 ({len(important_fields)}개):")
            for field in important_fields:
                print(f"  - '{field['text']}' (페이지 {field['page'] + 1})")
            
        except Exception as e:
            print(f"❌ 템플릿 분석 실패: {e}")
    
    print("\n🎉 템플릿 분석 완료!")

if __name__ == "__main__":
    analyze_template_fields() 