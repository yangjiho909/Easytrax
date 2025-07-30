#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 템플릿 기반 PDF 생성 디버깅
"""

import os
from datetime import datetime
from template_based_pdf_generator import template_pdf_generator

def debug_template_pdf_generation():
    """템플릿 기반 PDF 생성 디버깅"""
    
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
    
    print("🔍 템플릿 기반 PDF 생성 디버깅 시작")
    print(f"📋 테스트 데이터: {test_data}")
    
    # 1. 템플릿 분석
    print("\n1️⃣ 템플릿 분석 단계")
    try:
        template_info = template_pdf_generator.get_template_info('상업송장')
        print(f"✅ 템플릿 분석 성공")
        print(f"📄 페이지 수: {template_info.get('pages', 'N/A')}")
        print(f"🔍 발견된 필드: {list(template_info.get('fields', {}).keys())}")
        
        # 필드 상세 정보
        for field_name, field_info in template_info.get('fields', {}).items():
            print(f"  - {field_name}: {field_info.get('text', 'N/A')} (페이지 {field_info.get('page', 'N/A')})")
            
    except Exception as e:
        print(f"❌ 템플릿 분석 실패: {e}")
        return
    
    # 2. 데이터 매핑
    print("\n2️⃣ 데이터 매핑 단계")
    try:
        mapped_data = template_pdf_generator._map_data_to_template('상업송장', test_data)
        print(f"✅ 데이터 매핑 성공")
        print(f"📋 매핑된 데이터: {mapped_data}")
        
    except Exception as e:
        print(f"❌ 데이터 매핑 실패: {e}")
        return
    
    # 3. PDF 생성
    print("\n3️⃣ PDF 생성 단계")
    try:
        output_filename = f"debug_상업송장_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join("generated_documents", output_filename)
        
        print(f"📁 출력 경로: {output_path}")
        
        # 템플릿 기반 PDF 생성
        result_path = template_pdf_generator.generate_filled_pdf(
            '상업송장', 
            test_data, 
            output_path
        )
        
        print(f"📄 생성 결과 경로: {result_path}")
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ PDF 생성 성공: {result_path} ({file_size} bytes)")
            
            # 파일 크기 비교
            original_template = "uploaded_templates/상업송장(Commercial Invoice).pdf"
            if os.path.exists(original_template):
                original_size = os.path.getsize(original_template)
                print(f"📊 원본 템플릿 크기: {original_size} bytes")
                print(f"📊 생성된 PDF 크기: {file_size} bytes")
                print(f"📊 크기 차이: {file_size - original_size} bytes")
                
        else:
            print(f"❌ PDF 파일이 생성되지 않음")
            
    except Exception as e:
        print(f"❌ PDF 생성 실패: {e}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
    
    print("\n🎉 디버깅 완료!")

if __name__ == "__main__":
    debug_template_pdf_generation() 