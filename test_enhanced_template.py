#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 개선된 템플릿 기반 PDF 생성기 테스트
"""

import os
from datetime import datetime
from enhanced_template_pdf_generator import enhanced_template_pdf_generator

def test_enhanced_template_pdf():
    """개선된 템플릿 기반 PDF 생성 테스트"""
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "company_info": {
            "name": "한국식품공업(주)",
            "address": "서울시 강남구 테헤란로 123",
            "phone": "02-1234-5678",
            "email": "info@koreanfood.co.kr"
        },
        "product_info": {
            "name": "신라면",
            "code": "SR001",
            "quantity": 1000,
            "unit_price": 2.50,
            "weight": 500
        }
    }
    
    print("🧪 개선된 템플릿 기반 PDF 생성 테스트 시작")
    print(f"📋 테스트 데이터: {test_data}")
    
    # 사용 가능한 템플릿 확인
    templates = enhanced_template_pdf_generator.list_available_templates()
    print(f"📄 사용 가능한 템플릿: {templates}")
    
    # 각 템플릿으로 PDF 생성 테스트
    for doc_type in templates:
        print(f"\n📋 {doc_type} 생성 테스트...")
        
        try:
            # 템플릿 정보 확인
            template_info = enhanced_template_pdf_generator.get_template_info(doc_type)
            print(f"✅ 템플릿 분석 완료: {template_info.get('pages', 'N/A')} 페이지")
            print(f"🔍 템플릿 필드: {list(template_info.get('fields', {}).keys())}")
            
            # PDF 생성
            output_filename = f"enhanced_{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join("generated_documents", output_filename)
            
            result_path = enhanced_template_pdf_generator.generate_filled_pdf(
                doc_type, 
                test_data, 
                output_path
            )
            
            if os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"✅ {doc_type} 생성 성공: {result_path} ({file_size} bytes)")
                
                # 원본 템플릿과 크기 비교
                original_template = f"uploaded_templates/{enhanced_template_pdf_generator.templates[doc_type]}"
                if os.path.exists(original_template):
                    original_size = os.path.getsize(original_template)
                    print(f"📊 원본 템플릿 크기: {original_size} bytes")
                    print(f"📊 생성된 PDF 크기: {file_size} bytes")
                    print(f"📊 크기 차이: {file_size - original_size} bytes")
                    
            else:
                print(f"❌ {doc_type} 생성 실패: 파일이 생성되지 않음")
                
        except Exception as e:
            print(f"❌ {doc_type} 생성 중 오류: {e}")
            import traceback
            print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("\n🎉 개선된 템플릿 기반 PDF 생성 테스트 완료!")

if __name__ == "__main__":
    test_enhanced_template_pdf() 