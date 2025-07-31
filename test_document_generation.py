#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
서류생성 API 테스트 스크립트
"""

import requests
import json

def test_document_generation():
    """서류생성 API 테스트"""
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "selected_documents": ["상업송장", "포장명세서"],
        "company_info": {
            "name": "한국식품산업(주)",
            "address": "서울특별시 강남구 테헤란로 123",
            "phone": "02-1234-5678",
            "email": "info@koreafood.co.kr",
            "representative": "김대표"
        },
        "product_info": {
            "name": "신라면",
            "description": "매운맛 라면",
            "quantity": "1000",
            "unit_price": "5.00",
            "total_amount": "5000.00",
            "unit": "박스"
        },
        "buyer_info": {
            "name": "중국식품무역(주)",
            "address": "상하이시 푸동신구 456번지",
            "phone": "021-8765-4321",
            "notify_party": "중국식품무역(주)"
        },
        "transport_info": {
            "method": "해상운송",
            "mode": "해상운송",
            "origin": "부산항",
            "destination": "상하이항",
            "from_location": "부산항",
            "to_location": "상하이항",
            "departure_date": "2024-01-15",
            "vessel_flight": "EVER GIVEN 001W",
            "delivery_terms": "FOB 부산"
        },
        "payment_info": {
            "method": "신용장",
            "currency": "USD",
            "lc_number": "LC2024001",
            "lc_date": "2024-01-10",
            "reference": "REF001",
            "payment_terms": "신용장 90일"
        },
        "packing_details": {
            "method": "카톤박스 포장",
            "details": "카톤박스 포장",
            "material": "카톤",
            "size": "표준",
            "weight": "10kg",
            "total_weight": "10kg",
            "total_packages": "100",
            "package_count": "100",
            "package_type": "박스",
            "shipping_marks": "KOREA FOOD",
            "marks": "KOREA FOOD",
            "net_weight": "8kg",
            "gross_weight": "10kg",
            "dimensions": "30x20x15cm",
            "handling_notes": "습기 주의",
            "storage_conditions": "건조한 곳에 보관",
            "labels": "건조한 곳에 보관"
        },
        "customization": {
            "language": "한국어",
            "format": "표준"
        }
    }
    
    # API 호출
    url = "http://localhost:5000/api/document-generation"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 서류생성 API 테스트 시작...")
        print(f"📋 요청 데이터:")
        print(json.dumps(test_data, indent=2, ensure_ascii=False))
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"📡 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 호출 성공!")
            print(f"📄 생성된 서류: {result.get('generated_count', 0)}개")
            print(f"📁 PDF 파일: {result.get('pdf_files', {})}")
            print(f"🔗 다운로드 URL: {result.get('download_urls', {})}")
            
            # 각 서류 내용 출력
            if 'documents' in result:
                for doc_name, content in result['documents'].items():
                    print(f"\n📋 {doc_name}:")
                    print("-" * 50)
                    print(content)
                    print("-" * 50)
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"📋 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_document_generation() 